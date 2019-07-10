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
import utils

let doc = """
SiteBaker. Command line static website generator.

Usage:
  baker generate [--file <filename>] [--force]
  baker indexes [--posts=<num>] <directory>
  baker dump <filename>
  baker init [<dir>]
  baker micro
  baker test

Options:
  -h --help       Show this screen.
  --file          Generate a specific file.
  --force         Force re-generation, not just new files
  --version       Show version
  --posts=<posts> Posts per index page [default: 10]

Available commands:
  generate        Generate/render a file, or if no arguments given, all files with recent changes.
  indexes         Create the index pages for posts in a given directory.
  dump
  init            Setup a directory to use with baker.

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
        echo replaceEmoji("this is a test :thumbs_up: this is a test :zzz:")

    elif args["micro"]:
        microBlog()