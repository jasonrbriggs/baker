import os

import docopt

import config
import generator
import pages
import streams
import utils

let doc = """
SiteBaker. Command line static website generator.

Usage:
  baker generate [--file <filename>] [--force]
  baker dump <filename>
  baker init [<dir>]
  baker test

Options:
  -h --help     Show this screen.
  --version     Show version
"""

when isMainModule:
    let args = docopt(doc, version = "SiteBaker " & BakerVersion)

    if args["generate"]:
        if args["--file"]:
            generate($args["<filename>"])
        else:
            generateAll($args["--force"] == "true") 

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
        echo shortHash("this is a test")