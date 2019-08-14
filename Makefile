VERSION := $(shell grep version baker.nimble | grep -oP '"\K[^"\047]+(?=["\047])' )

all: clean compile

clean:
	echo $(VERSION)

compile:
	$(shell sed -i -e 's~BakerVersion[^"]*~BakerVersion=$(VERSION)~g' src/baker.nim.cfg )
	nimble install -y

#test: compile
#	nim c -p:. -r tests/basic_test
