BAKER=../baker

all:
	$(BAKER) generate $(FORCE)
	$(BAKER) indexes --posts=30 micro/
	$(BAKER) indexes journal/
	$(BAKER) compress $(FORCE)
	$(BAKER) tags
	$(BAKER) rss micro
	$(BAKER) rss journal
	$(BAKER) sitemap

force: 
	$(MAKE) FORCE="--force" all