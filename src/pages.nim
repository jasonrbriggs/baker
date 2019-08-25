import strformat
import nre
import os
import strtabs
import strutils
import times

import emoji
import markdown

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
        tags*: seq[string]
        htmlContent*: string
        shortLink*:string

let mentionRe = re"<a\s*[^>]*>@[^@]+@[^<]+</a>"
let likeRe = re"http[^\s]+\s+👍"
let urlRe = re"http[s]*:[^\s]+"


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


proc replaceLikes(html:string):string =
    var rtn = html
    var matches = findAll(html, likeRe)
    for match in matches:
        if find(match, "</a>") >= 0:
            continue
        let urls = findAll(match, urlRe)
        var shorturl = urls[0]
        shorturl = replace(shorturl, "https://", "")
        shorturl = replace(shorturl, "http://", "")
        rtn = replace(rtn, match, "<a class=\"u-like-of\" href=\"" & urls[0] & "\">" & shorturl & "</a> 👍")
    return rtn


proc replaceMentions(html:string):string =
    var rtn = html
    var matches = findAll(html, mentionRe)
    for match in matches:
        if find(match, "class=") >= 0:
            continue
        rtn = replace(rtn, match, replace(match, "<a ", "<a class=\"u-in-reply-to\" "))
    return rtn


proc readPage(path:string):(StringTableRef, string) =
    let s = readFile(path)

    var ss = nre.split(s, nre.re"\n\n|\r\n\r\n", maxSplit=2)

    var c:string = EmptyString
    var hdrs:StringTableRef = nil

    if not hasValidHeaders(ss[0]):
        hdrs = parseHeaders("")
        c = s
    else:
        hdrs = parseHeaders(ss[0])
        c = ss[1]
    return (hdrs, c)


proc mergeHeaders(h1:var StringTableRef, h2:StringTableRef) =
    for key,val in pairs(h2):
        if not hasKey(h1, key) and key != "banner-image":
            h1[key] = val


proc loadPage*(basedir:string, name:string):Page =
    var roothdrs:StringTableRef = nil
    var rootc:string = EmptyString
    let indextext = joinPath(basedir, "index.text") 
    if fileExists(indextext):
        (roothdrs, rootc) = readPage(indextext)
    else:
        (roothdrs, rootc) = readPage(joinPath(basedir, "index-page.text"))

    var (hdrs, c) = readPage(name)

    mergeHeaders(hdrs, roothdrs)

    c = replaceEmoji(c)

    var (dirname, filename, ext) = splitFile(name)

    var dn = findPathMatch(basedir, dirname, dirname)

    var pp = name
    if startsWith(name, basedir):
        pp = substr(name, len(basedir) + 1)
    var pb = dirname
    if startsWith(dirname, basedir):
        pb = substr(dirname, len(basedir))
        if not startsWith(pb, ForwardSlash):
            pb = ForwardSlash & pb

    let outputName = replace(name, ".text", ".html")

    var tags: seq[string] = @[]
    if hasKey(hdrs, "tags"):
        let ts = split(hdrs["tags"], ",")
        for t in ts:
            tags.add(strip(t))

    var html = markdown(c)
    html = replaceLikes(html)
    html = replaceMentions(html)
    return Page(name:name, basedir:basedir, dirname:dn, printedBase:pb, filename:filename, headers:hdrs, content:c, 
        bannerImage:EmptyString, outputName:outputName, tags:tags, htmlContent:html, shortLink:EmptyString)


proc initPage*(name:string, title:string, basedir:string):Page =
    let headers = {
        "title": title
    }.newStringTable
    return Page(name:name, basedir:basedir, headers:headers)


proc headersToString*(page:Page):string =
    var rtn = ""
    for key,val in pairs(page.headers):
        rtn &= key & ": " & val & NEWLINE
    return rtn & NEWLINE


proc printPage*(page:Page) =
    echo fmt"""Page: {page.name}
basedir: {page.basedir}
dirname: {page.dirname}
printed base: {page.printedBase}

{page.content}
"""