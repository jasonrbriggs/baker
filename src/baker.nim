import os

import docopt

import blog
import emoji
import generator
import pages
import streams
import strutils
import system
import times
import timezones
import utils
import zip/gzipfiles

let doc = """
Baker. Command line static website generator.

Usage:
  baker blog [--tags=<tags>] <title>...
  baker compress [--force]
  baker generate [--file <filename>] [--force]
  baker indexes [--posts=<num>] <directory>
  baker dump <filename>
  baker init [<dir>]
  baker jsonfeed <directory>
  baker micro
  baker rss <directory>
  baker sitemap
  baker test
  baker tags

Options:
  -h --help       Show this screen.
  --file          Generate a specific file.
  --force         Force re-generation, not just new files.
  --tags          Comma-separate list of tags, used for blog entries.
  --version       Show the version.
  --posts=<posts> Posts per index page [default: 10].

Available commands:
  blog            Generate a blog entry with the given title (and optionally tags).
  compress        Compress resource files (css, jpg).
  generate        Generate/render a file, or if no arguments given, all files with recent changes.
  indexes         Create the index pages for posts in a given directory.
  dump
  init            Setup a directory to use with baker.
  jsonfeed        Generate a json feed file for the given directory.
  micro           Generate a microblog entry (reads from standard-input, two newlines finishes entry).
  rss             Generate an RSS feed file for the given directory.
  sitemap         Generate the sitemap.xml file in the root directory.
  tags            Generate the tag cloud directory.
"""

when isMainModule:
    let args = docopt(doc, version = "Baker " & BakerVersion)

    if args["generate"]:
        if args["--file"]:
            generate($args["<filename>"])
        else:
            generateAll($args["--force"] == "true") 

    elif args["indexes"]:
        let dir = $args["<directory>"]
        var posts = 10
        if args["--posts"]:
            posts = parseInt($args["--posts"])
        generateIndexes(dir, posts)


    elif args["dump"]:
        let page = loadPage(".", $args["<filename>"])

        printPage(page)

    elif args["init"]:
        var dir:string = "."
        if args["<dir>"]:
            dir = $args["<dir>"]

        let makefile = joinPath(dir, "Makefile")
        if fileExists(makefile):
            echo "Already initialised"
            quit(1)
        else:
            var fs = newFileStream(makefile, fmWrite)
            fs.write(MAKEFILE)
            fs.close()

    elif args["test"]:
        let zone = tz"Europe/London"
        let dt = parse("2018-09-29T17:53:31+01:00", "yyyy-MM-dd\'T\'HH:mm:sszzz", zone)
        let ds = dt.format("yyyy-MM-dd\'T\'HH:mm:sszzz")
        let pos = ds.rfind(":")-1
        echo ds[0..pos] & ds[pos+2..len(ds)-1]

    elif args["micro"]:
        microBlog()

    elif args["tags"]:
        generateTags()

    elif args["compress"]:
        compressResourceFiles($args["--force"] == "true")

    elif args["rss"]:
        let dir = $args["<directory>"]
        generateFeed(dir)

    elif args["jsonfeed"]:
        let dir = $args["<directory>"]
        generateJsonFeed(dir)

    elif args["blog"]:
        var titleWords:seq[string] = @[]
        for word in @(args["<title>"]):
            titleWords.add(word)
        blog(join(titleWords, " "))

    elif args["sitemap"]:
        generateSitemap()