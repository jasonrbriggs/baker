BAKER=../../baker

all:
	$(BAKER) generate $(FORCE)
	$(BAKER) indexes --posts=30 micro/
	$(BAKER) indexes blog
	$(BAKER) compress $(FORCE)
	$(BAKER) tags
	$(BAKER) rss micro
	$(BAKER) jsonfeed micro
	$(BAKER) rss blog
	$(BAKER) jsonfeed blog
	$(BAKER) jsonfeed . --combined
	$(BAKER) sitemap

force: 
	$(MAKE) FORCE="--force" all