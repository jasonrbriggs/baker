import os

import docopt

import blog
import config
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
SiteBaker. Command line static website generator.

Usage:
  baker blog <title>...
  baker compress [--force]
  baker generate [--file <filename>] [--force]
  baker indexes [--posts=<num>] <directory>
  baker dump <filename>
  baker init [<dir>]
  baker micro
  baker rss <directory>
  baker test
  baker tags

Options:
  -h --help       Show this screen.
  --file          Generate a specific file.
  --force         Force re-generation, not just new files
  --version       Show version
  --posts=<posts> Posts per index page [default: 10]

Available commands:
  compress        Compress resource files (css, jpg)
  generate        Generate/render a file, or if no arguments given, all files with recent changes.
  indexes         Create the index pages for posts in a given directory.
  dump
  init            Setup a directory to use with baker.
  tags            Generate the tag cloud directory
"""

when isMainModule:
    let args = docopt(doc, version = "SiteBaker " & BakerVersion)

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

        let dotbaker = joinPath(dir, ".baker")
        if fileExists(dotbaker):
            echo "Already initialised"
            quit(1)
        else:
            echo "inited"
            var fs = newFileStream(dotbaker, fmWrite)
            fs.writeLine("")
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

    elif args["blog"]:
        var titleWords:seq[string] = @[]
        for word in @(args["<title>"]):
            titleWords.add(word)
        blog(join(titleWords, " "))