import strformat
import nre
import os
import strtabs
import strutils
import times

import utils


type
    Page* = object
        name*: string
        outputName*: string
        basedir*: string
        dirname*: string
        printedBase*: string
        filename*: string
        headers*: StringTableRef
        content*: string
        bannerImage*: string
        pageType*: string


proc hasValidHeaders(s:string):bool =
    if strip(s) != "":
        for line in nre.split(s, nre.re"\n|\r\n"):
            var keyval = nre.split(line, nre.re"\s*:\s*", 2)
            if len(keyval) == 2:
                return true
    return false


proc parseHeaders(s:string):StringTableRef =
    var hdrs = newStringTable()
    if strip(s) != "":
        for line in nre.split(s, nre.re"\n|\r\n"):
            var keyval = nre.split(line, nre.re"\s*:\s*", 2)
            hdrs[keyval[0]] = keyval[1]
    return hdrs


proc getHeader*(page:Page, name:string, default:string=""):string =
    if page.headers == nil or not hasKey(page.headers, name):
        return default
    return page.headers[name]


proc loadPage*(basedir:string, name:string):Page =
    let s = readFile(name)

    var ss = nre.split(s, nre.re"\n\n|\r\n\r\n", maxSplit=2)

    var c:string = EmptyString
    var hdrs:StringTableRef = nil

    if not hasValidHeaders(ss[0]):
        hdrs = parseHeaders("")
        c = s
    else:
        hdrs = parseHeaders(ss[0])
        c = ss[1]

    var (dirname, filename, ext) = splitFile(name)

    var dn = findPathMatch(basedir, dirname, dirname)

    var pp = name
    if startsWith(name, basedir):
        pp = substr(name, len(basedir) + 1)
    var pb = dirname
    if startsWith(dirname, basedir):
        pb = substr(dirname, len(basedir))
        if not startsWith(pb, "/"):
            pb = "/" & pb

    return Page(name:name, basedir:basedir, dirname:dn, printedBase:pb, filename:filename, headers:hdrs, content:c, bannerImage:EmptyString)


proc headersToString*(page:Page):string =
    var rtn = ""
    for key,val in pairs(page.headers):
        rtn &= key & ": " & val & "\n"
    return rtn & "\n"


proc printPage*(page:Page) =
    echo fmt"""Page: {page.name}
basedir: {page.basedir}
dirname: {page.dirname}
printed base: {page.printedBase}

{page.content}
"""