VERSION := $(shell grep version baker.nimble | grep -oP '"\K[^"\047]+(?=["\047])' )

export BAKER_DATETIME_OVERRIDE=2019-10-07T20:57:12+0100
export TESTSITE_DIR=test/testsite
export TEST_BAKER=../../baker

all: clean compile test

clean:
	rm -rf test/testsite

compile:
	$(shell sed -i -e 's~BakerVersion[^"]*~BakerVersion=$(VERSION)~g' src/baker.nim.cfg )
	nimble install -y

	export REPLACEMENT="`baker --help`"; \
	python -c "import re; s = open('README.md').read(); print(s.replace(re.search(r'Current command-line.*', s, re.DOTALL | re.MULTILINE).group(0), '''Current command-line:\n\n\`\`\`\n$${REPLACEMENT}\n\`\`\`'''))" > README.md.tmp
	mv README.md.tmp README.md

#test: compile
#	nim c -p:. -r tests/basic_test

test: clean
	cd test; ../baker init testsite
	cd ${TESTSITE_DIR}; ${TEST_BAKER} header --file index.text updated-time --set 2019-11-13T23:59:59+01:00
	cd ${TESTSITE_DIR}; ${TEST_BAKER} blog "This is a test post"
	cd ${TESTSITE_DIR}; echo "This is a test post" >> blog/2019/10/07/this-is-a-test-post.text
	cd ${TESTSITE_DIR}; ${TEST_BAKER} header --file blog/2019/10/07/this-is-a-test-post.text updated-time --set 2019-11-07T23:59:59+01:00
	cd ${TESTSITE_DIR}; echo "This is a test micro post" | ../../baker micro -
	cd ${TESTSITE_DIR}; ${TEST_BAKER} header --file micro/2019/10/07/205712.text updated-time --set 2019-11-07T23:59:59+01:00
	mkdir ${TESTSITE_DIR}/notebook; cp test/notebook.text ${TESTSITE_DIR}/notebook/
	cd ${TESTSITE_DIR}; ${TEST_BAKER} header --file notebook/notebook.text updated-time --set 2019-11-13T23:59:59+01:00
	cp src/resources/banner.jpg ${TESTSITE_DIR}/img/
	sed -i "s/BAKER=baker/BAKER=..\/..\/baker/g" ${TESTSITE_DIR}/Makefile
	cd ${TESTSITE_DIR}; make
	