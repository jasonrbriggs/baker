import httpclient
import strformat
import nre
import os
import streams
import strtabs
import strutils
import times

import emoji
import markdown
import ndb/sqlite

import db
import invoke
import utils


type
    Page* = object
        name*: string
        outputName*: string
        basedir*: string
        dirname*: string
        printedBase*: string
        filename*: string
        headerKeys*: seq[string]
        headers*: StringTableRef
        content*: string
        bannerImage*: string
        pageType*: string
        tags*: seq[string]
        htmlContent*: string
        shortLink*: string
        postedTime*: DateTime

let mentionRe = re"<a\s*[^>]*>@[^@]+@[^<]+</a>"
let likeRe = re"http[^\s]+\s+👍"
let urlRe = re"http[s]*:[^\s]+"
# required because double-space (newline in markdown) is not working any more
let emNewlineRe = re"_  \n"
let bracketNewlineRe = re"\)  "
let newlineRe = re"  \n"


proc hasValidHeaders(s:string):bool =
    if strip(s) != "":
        for line in nre.split(s, nre.re"\n|\r\n"):
            var keyval = nre.split(line, nre.re"\s*:\s*", 2)
            if len(keyval) == 2:
                return true
    return false


proc parseHeaders(s:string):(seq[string], StringTableRef) =
    var headers = newStringTable()
    var headerKeys: seq[string] = @[]
    if strip(s) != "":
        for line in nre.split(s, nre.re"\n|\r\n"):
            var keyval = nre.split(line, nre.re"\s*:\s*", 2)
            if len(keyval) > 1:
                add(headerKeys, keyval[0])
                headers[keyval[0]] = keyval[1]
    return (headerKeys, headers)


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
        let wmurl = getWebmentionUrl(urls[0])
        var class = "u-like-of"
        if wmurl == EmptyString:
            class = ""
        rtn = replace(rtn, match, "<a " & class & "href=\"" & urls[0] & "\">" & shorturl & "</a> 👍")
    return rtn


proc replaceMentions(html:string):string =
    var rtn = html
    var matches = findAll(html, mentionRe)
    for match in matches:
        if find(match, "class=") >= 0:
            continue
        # exclusion for twitter since it doesn't work with federation
        if find(match, "twitter.com") >= 0:
            continue 
        rtn = replace(rtn, match, replace(match, "<a ", "<a class=\"u-in-reply-to\" "))
    return rtn


proc replaceNewlines(html:string):string =
    # edge case "_something_<br />" doesn't get replaced by markdown

    var rtn = nre.replace(html, emNewlineRe, "_ <br />\n")
    rtn = nre.replace(rtn, bracketNewlineRe, ") <br />\n")
    # other cases
    rtn = nre.replace(rtn, newlineRe, "<br />\n")
    return rtn


proc readPage(path:string):(seq[string], StringTableRef, string) =
    let s = readFile(path)

    var ss = nre.split(s, nre.re"\n\n|\r\n\r\n", maxSplit=2)

    var c:string = EmptyString
    var headerKeys:seq[string] = @[]
    var headers:StringTableRef = nil

    if not hasValidHeaders(ss[0]):
        (headerKeys, headers) = parseHeaders("")
        c = s
    else:
        (headerKeys, headers) = parseHeaders(ss[0])
        if len(ss) == 1:
            c = ""
        else:
            c = ss[1]
    return (headerKeys, headers, c)


proc mergeHeaders(h1:var StringTableRef, h2:StringTableRef) =
    for key,val in pairs(h2):
        if not hasKey(h1, key) and key != "banner-image" and key != "type" and key != "updated-time":
            h1[key] = val


proc loadPage*(basedir:string, name:string, preProcess:bool = true):Page =
    if not fileExists(name):
        echo "Page " & name & " does not exist"
        quit 1
    var roothdrkeys: seq[string] = @[] 
    var roothdrs:StringTableRef = nil
    var rootc:string = EmptyString
    let indextext = joinPath(basedir, "index.text") 
    if fileExists(indextext):
        (roothdrkeys, roothdrs, rootc) = readPage(indextext)
    else:
        (roothdrkeys, roothdrs, rootc) = readPage(joinPath(basedir, "index-page.text"))

    var (headerKeys, headers, c) = readPage(name)

    if preProcess:
        mergeHeaders(headers, roothdrs)
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

    let outputName = replace(name, DOT_TEXT_EXT, DOT_HTML_EXT)

    var tags: seq[string] = @[]
    if hasKey(headers, "tags"):
        let ts = split(headers["tags"], ",")
        for t in ts:
            tags.add(strip(t))

    var pt = EmptyString
    if hasKey(headers, "type"):
        pt = headers["type"]

    var postedTime = getCurrentDateTime()
    if hasKey(headers, "posted-time"):
        postedTime = parseDateTime(headers["posted-time"])

    var html = EmptyString
    if preProcess:
        c = processExecBlocks(dirname, filename, c)

        html = replaceNewlines(c)
        html = markdown(html, initGfmConfig())
        html = replaceLikes(html)
        html = replaceMentions(html)

    return Page(name:name, basedir:basedir, dirname:dn, printedBase:pb, filename:filename, headers:headers, headerKeys:headerKeys, content:c, 
        bannerImage:EmptyString, pageType:pt, outputName:outputName, tags:tags, htmlContent:html, shortLink:EmptyString, postedTime:postedTime)


proc savePage(page:Page) =
    let textname = replace(page.outputName, DOT_HTML_EXT, DOT_TEXT_EXT)
    var output: seq[string] = @[]
    for k in page.headerKeys:
        add(output, k & ": " & page.headers[k])
    add(output, "")
    add(output, page.content)
    var fs = newFileStream(textname, fmWrite)
    fs.write(join(output, "\n"))
    fs.close()


proc initPage*(name:string, title:string, basedir:string):Page =
    let pt = getCurrentDateTime()
    let headers = {
        "title": title,
        "posted-time": formatDateTime(pt)
    }.newStringTable
    return Page(name:name, basedir:basedir, headers:headers, postedTime:pt)


proc headersToString*(page:Page):string =
    var rtn: seq[string] = @[]
    for key,val in pairs(page.headers):
        add(rtn, key & ": " & val)
    return join(rtn, "\n")


proc getHeader*(dir:string, filename:string, header:string):string =
    let pg = loadPage(dir, filename)
    if header == "":
        return headersToString(pg)
    if not hasKey(pg.headers, header):
        echo "Header " & header & " not found"
        quit 1
    return pg.headers[header]


proc setHeader*(dir:string, filename:string, header:string, newvalue:string) =
    var pg = loadPage(dir, filename, false)
    if not hasKey(pg.headers, header):
        add(pg.headerKeys, header)
    pg.headers[header] = newvalue
    savePage(pg)


proc printPage*(page:Page) =
    echo fmt"""Page: {page.name}
basedir: {page.basedir}
dirname: {page.dirname}
printed base: {page.printedBase}

{page.content}
"""


proc loadRootPage*(rootdir:string):Page = 
    var indexpage = "index-page.text"
    if not fileExists(indexpage):
        indexpage = "index.text"

    return loadPage(rootdir, indexpage)


proc addPage*(rootdir:string, page:Page) =
    let db = openDatabase(rootdir)
    let val = db.getValue(string, sql"SELECT url FROM pages WHERE url=?", page.outputName)
    if isNone(val) and hasKey(page.headers, "posted-time"):
        let postedtime = page.headers["posted-time"]
        let dt = formatDateTimeNoTz(parseDateTime(postedtime))
        db.exec(sql"insert into pages (url, shorturl, created_date) values (?, ?, ?)", page.outputName, page.shortLink, dt)

    db.close()


proc getLastModification*(page:Page): DateTime =
    if hasKey(page.headers, "updated-time"):
        let updatedtime = page.headers["updated-time"]
        return parseDateTime(updatedtime)
    let textname = replace(page.outputName, DOT_HTML_EXT, DOT_TEXT_EXT)
    return utc(getLastModificationTime(textname))


proc federatePages*(rootdir:string, federate_target_url:string, dir:string, offset_days:int) =
    echo "Federate new pages to " & federate_target_url
    echo "  - looking for webmention link"
    var wmurl = getWebmentionUrl(federate_target_url)
    if wmurl == EmptyString:
        for x in 0..5:
            sleep(1000)
            # try again, seem to get an occasional failure
            wmurl = getWebmentionUrl(federate_target_url)
            if wmurl != EmptyString:
                break
    
    if wmurl == EmptyString:
        echo "  - error: no webmention link found for: " & federate_target_url
        quit(1)
    else:
        echo "  - found webmention url: " & wmurl

    let rootpage = loadRootPage(rootdir)
    let url = rootpage.headers["url"]

    let offset_date = formatDateZeroTime(now() - initDuration(days=offset_days))
    
    var count = 0
    var client = newHttpClient()
    let db = openDatabase(rootdir)
    let wheredir = dir & "%"
    try:
        for r in db.rows(sql"SELECT p.url FROM pages p where created_date > ? and url like ? and not exists (select 1 from federated f where f.url = p.url and f.federated_to = ?)",
                offset_date, wheredir, federate_target_url):
            let page = replace(r[0].s, DOT_HTML_EXT, DOT_TEXT_EXT)
            if not fileExists(page):
                continue

            let pg = loadPage(rootdir, page)
            if pg.pageType == "page":
                continue

            let pageUrl = r[0].s

            let fullUrl = joinUrlPaths(url, pageUrl)

            var resp = client.request(fullUrl, httpMethod = HttpHead)
            let pageStatus = parseHttpStatus(resp.status)
            if pageStatus == 404:
                echo "  - warning: can't federate " & pageUrl & " (page not found - did you sync to your site?)"
                continue

            echo "  - federating " & fullUrl
            let body = "source=" & fullUrl & "&target=" & federate_target_url
            resp = client.request(wmurl, httpMethod = HttpPost, body = $body)

            let fedStatus = parseHttpStatus(resp.status)
            if fedStatus >= 400:
                echo "  - an error occurred federating " & pageUrl & ", status " & resp.status
                echo resp.headers.`$`
                echo resp.body
                quit(1)

            echo "    * done (status: " & resp.status & ")"
            let fedDate = formatDateTimeNoTz(now())
            db.exec(sql"insert into federated values (?, ?, ?)", pageUrl, federate_target_url, fedDate)
            inc(count)

        if count == 0:
            echo "  - no pages found to federate"
    
    finally:
        db.close()
