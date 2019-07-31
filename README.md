baker
=====

Baker is a simple static site generator written with [nim](https://nim-lang.org), the [proton](https://github.com/jasonrbriggs/proton) template engine for templating, and [markdown](http://daringfireball.net/projects/markdown/‎) for content.

Quick Start
-----------

Install Baker using the following command:
```
    nimble install baker
```

Create the skeleton of a new site by running the following:
```
    baker init mysite
```

A new directory (mysite) is created, containing a basic directory structure, and templates.

Create a new blog entry, by running the blog command:
```
    baker blog This is a test post title
```

Create a microblog entry by running:
```
	baker micro
```
Enter the text for your microblog post and hit enter twice to end the editing process.

Generate the html files for your site (including sitemap, rss feed, etc) using `make` (for newly changed files),
or `make force` (to regenerate everything).
