baker
=====

Baker is a simple static site generator written with [nim](https://nim-lang.org), the [proton](https://github.com/jasonrbriggs/proton) template engine for templating, and [markdown](http://daringfireball.net/projects/markdown/‎) for content.

Features
--------

* Static site generation (obviously)
* Generate site from a Makefile (See the test site for an [example](https://github.com/jasonrbriggs/baker/blob/master/test/testsite/Makefile))
* Create blog or microblog posts
* Resource compression (css, jpg)
* Generate index pages (i.e. an index of blog or microblog - effectively multiple posts per page)
* RSS generation
* JSON feed generation
* Sitemap generation
* Tag pages (like index pages, with multiple posts per page, but by tag)
* Federate posts to the [fediverse](https://en.wikipedia.org/wiki/Fediverse) via webmention (through sites such as [fed.brid.gy](https://fed.brid.gy/))
* Jupyter-style code execution in pages (basic support at the moment, see [here](https://github.com/jasonrbriggs/baker/blob/master/test/testsite/notebook/notebook.text) for an example)


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

Current command-line:

```
Baker. Command line static website generator.

Usage:
  baker blog <title> [--taglist <tags>]
  baker compress [--force]
  baker federate <targeturl> <directory> [--days <days>]
  baker generate [--file <filename>] [--force]
  baker header --file <filename> [<header>] [--set <newvalue>]
  baker indexes [--posts <num>] <directory>
  baker dump <filename>
  baker init [<dir>]
  baker jsonfeed <directory>
  baker micro [--ignoremaxlength] [-]
  baker rss <directory>
  baker sitemap
  baker testserver [--port <port>]
  baker tags

Options:
  -h --help           Show this screen.
  --days              Number of days to federate (new posts only) [default: 1].
  --file              Generate a specific file.
  --force             Force re-generation, not just new files.
  --ignoremaxlength   Ignore the max length for a micro blog and generate anyway.
  --tags              Comma-separate list of tags, used for blog entries.
  --version           Show the version.
  --posts <posts>     Posts per index page [default: 10].
  --port <port>       Port to use with the testserver [default: 8000].
  --taglist <tags>    Comma separated list of tags [default: ""]

Available commands:
  blog                Generate a blog entry with the given title (and optionally tags).
  federate            Federate new posts (within a number of days) to the given target url using webmention.
  compress            Compress resource files (css, jpg).
  generate            Generate/render a file, or if no arguments given, all files with recent changes.
  indexes             Create the index pages for posts in a given directory.
  dump                Dump detail about a page .text file (for debugging purposes, mostly).
  init                Setup a directory to use with baker.
  jsonfeed            Generate a json feed file for the given directory.
  micro               Generate a microblog entry (reads from standard-input, two newlines finishes entry).
  rss                 Generate an RSS feed file for the given directory.
  sitemap             Generate the sitemap.xml file in the root directory.
  tags                Generate the tag cloud directory.
  testserver          Run a bare-bones webserver, for testing the generated files.
```
