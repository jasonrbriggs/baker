import math
import os
import re
import strutils
import times

import generator
import utils

const
    MAX_MICROBLOG_LENGTH:int=500

let AT_LINK_RE = re.re("\\@[^@]+\\@[^\\s]+")

proc blog*(title:string) =
    let n = now()
    let dir = joinUrlPaths("journal", n.format("yyyy/MM/dd"))
    let name = toLowerAscii(multiReplace(title, ("\"", ""), ("'", ""), (":", ""), (" ", "-"), ("&", "and")))
    let filepath = joinUrlPaths(dir, name) & ".text"

    createDir(dir)
    var pout = open(filepath, fmWrite)
    write(pout, "title: " & title & "\n")
    write(pout, "posted-time: " & formatDateTime(n) & "\n")
    write(pout, "tags: \n")
    write(pout, "\n\n")
    close(pout)


proc microBlog*() =
    var input = ""
    while true:
        let line = readLine(stdin)
        if line == EmptyString:
            break
        if input != "":
            input = input & NEWLINE
        input = input & line

    if strip(input) == "":
        echo "Nothing to post"
        return

    let inputlen = len(input)
    if inputlen > MAX_MICROBLOG_LENGTH:
        echo "Micro entry is > " & MAX_MICROBLOG_LENGTH.`$` & " characters, consider reposting as:"
        echo ""
        let postsize = MAX_MICROBLOG_LENGTH-10
        let posts = int(ceil(inputlen / postsize))
        var startpos = 0
        var endpos = 0
        for x in 1..posts:
            echo "Post #" & x.`$`
            echo ""
            endpos = min(x * postsize, inputlen - 1)
            if x < posts:
                let wspos = rfind(input, Whitespace, endpos)
                if endpos - wspos < 30:
                    endpos = wspos
            let post = strip(input[startpos..endpos])
            startpos = endpos
            if x == posts:
                echo post & " (" & x.`$` & "/" & posts.`$` & ")"
            else:
                echo post & "... (" & x.`$` & "/" & posts.`$` & ")"
            echo ""
        return


    let at_matches = findAll(input, AT_LINK_RE)

    let n = now()
    let dir = joinUrlPaths("micro", n.format("yyyy/MM/dd"))
    let name = n.format("HHmmss") & ".text"

    let filepath = joinUrlPaths(dir, name)

    createDir(dir)
    let ts = n.format("dd MMM yyyy HH:mm:ss")

    var pout = open(filepath, fmWrite)
    write(pout, "title: Microblog posted at " & ts & "\n")
    write(pout, "type: micro-post\n")
    write(pout, "posted-time: " & n.format(DATETIME_FORMAT) & "\n")
    write(pout, "\n")
    write(pout, input)
    close(pout)

    generate(filepath)

    let index = "micro/index.text"
    if not fileExists(index):
        pout = open(index, fmWrite)
        write(pout, "title: Microblog\n")
        write(pout, "posted-time: " & n.format(DATETIME_FORMAT) & "\n")
        write(pout, "tags: \n")
        write(pout, "\n\n")
        close(pout)

    generateIndexes("micro", 50)