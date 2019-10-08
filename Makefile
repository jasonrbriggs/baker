VERSION := $(shell grep version baker.nimble | grep -oP '"\K[^"\047]+(?=["\047])' )

export BAKER_DATETIME_OVERRIDE=2019-10-07T20:57:12+0100

all: clean compile

clean:
	rm -rf test/testsite

compile:
	$(shell sed -i -e 's~BakerVersion[^"]*~BakerVersion=$(VERSION)~g' src/baker.nim.cfg )
	nimble install -y

#test: compile
#	nim c -p:. -r tests/basic_test

test: clean
	cd test; ../baker init testsite
	cd test/testsite; ../../baker blog "This is a test post"
	cd test/testsite; echo "This is a test post" >> blog/2019/10/07/this-is-a-test-post.text
	cd test/testsite; echo "This is a test micro post" | ../../baker micro -
	cd test/testsite; make