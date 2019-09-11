import algorithm
import json
import lists
import math
import os
import sequtils
import strformat
import strtabs
import strutils
import tables
import times
import zip/gzipfiles

import proton

import db
import emoji
import pages
import utils
import whistle

var template_dir_mappings = newStringTable()
var template_mappings = tables.initTable[string,Table[string,Template]]()


proc setValueFromHeader(tmp:Template, page:Page, header:string, eid:string) =
    if hasKey(page.headers, header):
        setvalue(tmp, eid, page.headers[header])


proc setAttributeFromHeader(tmp:Template, page:Page, header:string, aid:string, attr:string) =
    if hasKey(page.headers, header):
        setattribute(tmp, aid, attr, page.headers[header])


proc setPostedTime(tmp:Template, page:Page) =
    if hasKey(page.headers, "posted-time"):
        let dt = parseDateTime(page.headers["posted-time"])
        let dateonly = dt.format("dd MMM, yyyy")
        let timeonly = dt.format("hh:mm:ss")
        setvalue(tmp, "post-date-time", page.headers["posted-time"])
        setvalue(tmp, "micro-rel-link", page.headers["posted-time"])
        setvalue(tmp, "micro-link", page.headers["posted-time"])
        setattribute(tmp, "post-date-time", "datetime", page.headers["posted-time"])
        setattribute(tmp, "micro-rel-link", "datetime", page.headers["posted-time"])
        setattribute(tmp, "micro-link", "datetime", page.headers["posted-time"])
        setvalue(tmp, "post-date", dateonly)
        setvalue(tmp, "post-time", timeonly)


proc pickBannerImage(page:var Page) =
    page.bannerImage = EmptyString
    if hasKey(page.headers, "banner-image"):
        page.bannerImage = page.headers["banner-image"]
    else:
        let rootdir = getRootDir(page.dirname)
        let bannerdir = joinPath(rootdir, "img", "banners")
        if dirExists(bannerdir):
            var banners: seq[string] = @[]
            for kind, path in walkDir(bannerdir):
                if not endsWith(path, "gz"):
                    banners.add(path[len(rootdir)..len(path)-1])
            sort(banners, system.cmp)
            let perc = shortHash(page.headers["title"])
            let pos = int(round(perc * float32(len(banners))))
            page.bannerImage = banners[len(banners)-1]
            if pos < len(banners):
                page.bannerImage = banners[pos]


proc setBannerImage(tmp:Template, page:Page) =
    if page.bannerImage != EmptyString:
        setattribute(tmp, "banner-image", "src", page.bannerImage)
    else:
        hide(tmp, "banner-image")


proc setTagLinks(tmp:Template, page:Page) =
    if hasKey(page.headers, "tags"):
        var tags = split(page.headers["tags"], ",")
        sort(tags, system.cmp)
        setattribute(tmp, "keywords", "content", join(tags, ","))
        repeat(tmp, "taglinks", len(tags))
        for i in 0..len(tags)-1:
            setvalue(tmp, "taglink", tags[i], indexof(i))
            setattribute(tmp, "taglink", "href", "/tags/" & tags[i] & DOT_HTML_EXT, indexof(i))
    else:
        hide(tmp, "taglinks")
        hide(tmp, "taglinks-image")


proc addImageShadowStyle(tmp:Template, page:Page) =
    if hasKey(page.headers, "shadow"):
        var images = split(page.headers["shadow"], ",")
        for image in images:
            prependHtml(tmp, "content", """
<style type="text/css">
[alt="""" & image & """"] {
-moz-box-shadow: 4px 4px 5px #aaaaaa;
-webkit-box-shadow: 4px 4px 5px #aaaaaa;
box-shadow: 4px 4px 5px #aaaaaa;
/* For IE 8 */
-ms-filter: "progid:DXImageTransform.Microsoft.Shadow(Strength=4, Direction=135, Color='#aaaaaa')";
/* For IE 5.5 - 7 */
filter: progid:DXImageTransform.Microsoft.Shadow(Strength=4, Direction=135, Color='#aaaaaa');
}
</style>
""")


proc generateContent(page:var Page, tmps:Table[string,Template]):Template =
    let content_template = gettemplate(joinPath(template_dir_mappings[page.dirname], page.pageType & "-content.html"), true, tmps)
    setValueFromHeader(content_template, page, "title", "title")
    setValueFromHeader(content_template, page, "sub-title", "sub-title")
    setvalue(content_template, "content", page.htmlContent)
    setPostedTime(content_template, page)
    setTagLinks(content_template, page)
    addImageShadowStyle(content_template, page)
    setattribute(content_template, "permalink-url", "href", ForwardSlash & page.outputName)
    setattribute(content_template, "micro-rel-link", "href", ForwardSlash & page.outputName)
    setattribute(content_template, "micro-link", "href", joinUrlPaths(page.headers["url"], page.outputName))

    let rootdir = getRootDir(page.dirname)    
    addShortenedUrl(rootdir, page)
    if page.shortLink != EmptyString:
        setattribute(content_template, "shortlink-url", "href", ForwardSlash & page.shortLink)

    addPage(rootdir, page)

    return content_template


proc generatePageCommon(page:Page, tmps:Table[string,Template], tmp:Template) =
    # head setup
    let head_template = gettemplate(joinPath(template_dir_mappings[page.dirname], "head.html"), true, tmps)
    setValueFromHeader(tmp, page, "title", "title")
    setValueFromHeader(tmp, page, "sub-title", "sub-title")
    setValueFromHeader(head_template, page, "title", "title")
    setValueFromHeader(head_template, page, "sub-title", "sub-title")
    setattribute(head_template, "generator", "content", "SiteBaker " & BakerVersion)
    setTagLinks(head_template, page)
    setPostedTime(head_template, page)

    # header setup
    let header_template = gettemplate(joinPath(template_dir_mappings[page.dirname], "header.html"), true, tmps)
    setBannerImage(header_template, page)
    setTagLinks(header_template, page)
    setattribute(header_template, "permalink-url", "href", page.outputName)

    # footer setup
    let foot_template = gettemplate(joinPath(template_dir_mappings[page.dirname], "foot.html"), true, tmps)
    setBannerImage(foot_template, page)
    setattribute(foot_template, "permalink-url", "href", page.outputName)

    setBannerImage(tmp, page)
    replace(tmp, "head", head_template)
    replace(tmp, "header", header_template)
    replace(tmp, "footer", foot_template)



proc generatePage(page:Page, tmps:Table[string,Template]):Template =
    let page_template = gettemplate(joinPath(template_dir_mappings[page.dirname], page.pageType & DOT_HTML_EXT), true, tmps)
    generatePageCommon(page, tmps, page_template)
    return page_template


proc loadTemplates(page:Page): Table[string,Template] =
    if not hasKey(template_dir_mappings, page.dirname):
        var tmpdir = findFileUp(page.dirname, "templates")
        if tmpdir == EmptyString:
            raise newException(OSError, "No templates directory found")
        template_dir_mappings[page.dirname] = tmpdir
        let tmps = tables.initTable[string,Template]()
        template_mappings[page.dirname] = tmps

    return template_mappings[page.dirname]


proc writePage(name:string, tmp:Template) = 
    var pout = open(name, fmWrite)
    print(pout, tmp)
    close(pout)


proc getPrevNextPage(name:string, page_num:int, total:int):(string, string) =
    let prev_num = page_num - 1
    let prev_page = if prev_num > 0: "-" & prev_num.`$` else: ""
    let prev = replace(name, DOT_HTML_EXT, prev_page & DOT_HTML_EXT)
    let next_num = page_num + 1
    let next = replace(name, DOT_HTML_EXT, "-" & next_num.`$` & DOT_HTML_EXT)
    if page_num == 0:
        if next_num < total:
            return (EmptyString, next)
        else:
            return (EmptyString, EmptyString)
    elif next_num >= total:
        return (prev, EmptyString)
    else:
        return (prev, next)


proc writeIndexPage(name:string, tmp:Template, page_num:int, total_pages:int) =
    let (prev, next) = getPrevNextPage(name, page_num, total_pages)
    if prev != EmptyString:
        setattribute(tmp, "prevpage", "href", ForwardSlash & prev)
    else:
        hide(tmp, "prevpage")
        hide(tmp, "pagelinksep")
    if next != EmptyString:
        setattribute(tmp, "nextpage", "href", ForwardSlash & next)
    else:
        hide(tmp, "nextpage")
        hide(tmp, "pagelinksep")

    if page_num > 0:
        writePage(replace(name, DOT_HTML_EXT, "-" & page_num.`$` & DOT_HTML_EXT), tmp)
    else:
        writePage(name, tmp)


proc generate*(filename:string) =
    var page = loadPage(".", filename)

    if hasKey(page.headers, "type"):
        page.pageType = page.headers["type"]
    else:
        page.pageType = "post"

    pickBannerImage(page)

    let tmps = loadTemplates(page)

    let page_template = generatePage(page, tmps)

    # page content setup
    let content_template = generateContent(page, tmps)
    replace(page_template, "post-content", content_template)

    hide(page_template, "prevpage")
    hide(page_template, "nextpage")
    hide(page_template, "pagelinksep")

    var cout = open(replace(page.outputName, DOT_HTML_EXT, "-content.html"), fmWrite)
    print(cout, content_template)
    close(cout)

    var shortlinkInfo = EmptyString
    if page.shortLink != EmptyString:
        shortLinkInfo = " (" & page.shortLink & ")"
    echo " . " & page.outputName & shortlinkInfo
    writePage(page.outputName, page_template)


proc generateAll*(force:bool) =
    let cd = getCurrentDir()
    let cdl = len(cd)+1
    for path in walkDirRec(cd):
        let p = path[cdl..len(path)-1]
        if endsWith(p, "index-page.text"):
            continue
        if endsWith(p, "text"):
            let html = replace(p, DOT_TEXT_EXT, DOT_HTML_EXT)
            if force or not fileExists(html) or fileNewer(p, html):
                generate(p)


proc generateIndexes*(directory:string, postsPerPage:int) =
    var files: seq[string] = @[]
    for path in walkDirRec(directory):
        if contains(path, "-content.html"):
            add(files, path)
    sort(files, system.cmp, SortOrder.Descending)

    var page = loadPage(directory, joinPath(directory, "index-page.text"))
    page.name = "index"
    page.outputName = replace(page.outputName, "index-page", "index")
    if hasKey(page.headers, "type"):
        page.pageType = page.headers["type"]
    else:
        page.pageType = "post"
    pickBannerImage(page)

    let tmps = loadTemplates(page)
    var page_template = generatePage(page, tmps)

    let total_files = len(files)
    let total_pages = int(round(total_files / postsPerPage))

    echo "Generating index"
    echo "    - total posts = " & total_files.`$`
    echo "    - total pages = " & total_pages.`$`

    var page_num = 0

    repeat(page_template, "posts", postsPerPage)
    var post = 0
    for x in 0..len(files)-1:
        let content = readFile(files[x])
        replaceHtml(page_template, "post-content", content, indexof(post))

        inc(post)
        if post >= postsPerPage:
            writeIndexPage(page.outputName, page_template, page_num, total_pages)
            post = 0
            inc(page_num)
            page_template = generatePage(page, tmps)
            repeat(page_template, "posts", postsPerPage)

    if post > 0:
        writeIndexPage(page.outputName, page_template, page_num, total_pages)


proc generateTags*() =
    let cd = getCurrentDir()
    let cdl = len(cd)+1
    var tagNames: seq[string] = @[]
    var tags = tables.initTable[string,seq[string]]()
    for path in walkDirRec(cd):
        let p = path[cdl..len(path)-1]
        if endsWith(p, "text"):
            let page = loadPage(".", p)
            if len(page.tags) > 0:
                for tag in page.tags:
                    if tag == EmptyString:
                        continue
                    let t = replace(tag, " ", "-")
                    if not hasKey(tags, t):
                        tags[t] = @[]
                    tags[t].add(p) 
                    if not (t in tagNames):
                        tagNames.add(t)
    sort(tagNames, system.cmp)

    if not dirExists("tags"):
        createDir("tags")

    var page = initPage("tags", "Tags", ".")
    let tmps = loadTemplates(page)

    let tmp = gettemplate(joinPath(template_dir_mappings[page.dirname], "tags.html"), true, tmps)

    repeat(tmp, "tags", len(tagNames))
    for x in 0..len(tagNames)-1:
        let tag = tagNames[x]
        setvalue(tmp, "tag", tag, indexOf(x))
        setattribute(tmp, "tag", "href", "/tags/" & toLowerAscii(tag) & DOT_HTML_EXT, indexOf(x))
        let count = len(tags[tag])
        if count >= 20:
            setattribute(tmp, "tag", "class", "tag20", indexOf(x))
        elif count >= 15:
            setattribute(tmp, "tag", "class", "tag15", indexOf(x))
        elif count >= 10:
            setattribute(tmp, "tag", "class", "tag10", indexOf(x))
        elif count >= 5:
            setattribute(tmp, "tag", "class", "tag5", indexOf(x))

    pickBannerImage(page)
    generatePageCommon(page, tmps, tmp)

    writePage("tags/index.html", tmp)

    for tag in tagNames:
        let pages: seq[string] = tags[tag]
        var actualPages: seq[string] = @[]
        for page in pages:
            let p = replace(page, DOT_TEXT_EXT, "-content.html")
            if fileExists(p):
                actualPages.add(p)
        var tagPage = initPage(tag, tag, ".")
        let ltag = toLowerAscii(tag)
        let tagTmp = gettemplate(joinPath(template_dir_mappings[page.dirname], "tag.html"), true, tmps)
        repeat(tagTmp, "posts", len(actualPages))

        for x in 0..len(actualPages)-1:
            let content = readFile(actualPages[x])
            replaceHtml(tagTmp, "post-content", content, indexof(x))

        pickBannerImage(tagPage)
        generatePageCommon(tagPage, tmps, tagTmp)
        writePage("tags/" & ltag & DOT_HTML_EXT, tagTmp)


proc compressResourceFiles*(force:bool) = 
    echo "Compressing resource files (force=" & force.`$` & ")"
    let cd = getCurrentDir()
    let cdi = len(cd)+1
    for path in walkDirRec(cd):
        if endsWith(path, "jpg") or endsWith(path, "css"):
            let gzpath = path & "gz"
            if force or not fileExists(gzpath) or fileNewer(path, gzpath):
                let fin = readFile(path)
                let gz = newGzFileStream(gzpath, fmWrite)
                write(gz, fin)
                gz.close()
                echo " . " & path[cdi..len(path)-1]
    echo "complete"


proc loadFeedFiles(directory:string):(Page, seq[string]) =
    var files: seq[string] = @[]
    let cd = getCurrentDir()
    let cdi = len(cd)+1
    for path in walkDirRec(directory):
        if contains(path, "-content.html"):
            add(files, replace(path, "-content.html", DOT_TEXT_EXT))
    sort(files, system.cmp, SortOrder.Descending)

    let rootpage = loadPage(".", joinPath(directory, "index-page.text"))

    return (rootpage, files)


proc generateFeed*(directory:string) =
    var (rootpage, files) = loadFeedFiles(directory)
    let url = rootpage.headers["url"]

    let tmps = loadTemplates(rootpage)
    let tmp = gettemplate(joinPath(template_dir_mappings[rootpage.dirname], "rss.xml"), true, tmps)

    repeat(tmp, "items", len(files))
    setvalue(tmp, "channel-title", rootpage.headers["title"])
    setvalue(tmp, "channel-link", url)
    setvalue(tmp, "channel-description", rootpage.headers["description"])
    setattribute(tmp, "atom-link", "href", joinUrlPaths(url, directory, "feed.xml"))

    var x = 0
    for file in files:
        let page = loadPage(".", file)

        let htmlUrl = joinUrlPaths(url, replace(file, DOT_TEXT_EXT, DOT_HTML_EXT))
        let pos = indexOf(x)
        setvalue(tmp, "title", page.headers["title"], pos)
        setvalue(tmp, "link", htmlUrl, pos)
        setvalue(tmp, "description", "<![CDATA[" & page.htmlContent & "]]>", pos)

        let dt = parseDateTime(page.headers["posted-time"])
        let fdt = formatDateTimeRss(dt)
        setvalue(tmp, "pubdate", fdt, pos)
        setvalue(tmp, "guid", replace(htmlUrl, DOT_HTML_EXT, EmptyString), pos)

        if x == 0:
            setvalue(tmp, "lastbuild", fdt)

        inc(x)

    writePage(joinPath(directory, "feed.xml"), tmp)


proc generateJsonFeed*(directory:string) =
    var (rootpage, files) = loadFeedFiles(directory)

    let url = rootpage.headers["url"]

    let filename = joinPath(directory, "feed.json")

    var jsonfeed = %*{
        "version": "https://jsonfeed.org/version/1",
        "title": rootpage.headers["title"],
        "home_page_url": url,
        "feed_url": joinUrlPaths(url, directory, "feed.json"),
        "items": nil
    }

    var items = newJArray()

    for file in files:
        let page = loadPage(".", file)

        let htmlUrl = joinUrlPaths(url, replace(file, DOT_TEXT_EXT, DOT_HTML_EXT))
        let dt = parseDateTime(page.headers["posted-time"])
        let fdt = formatDateTimeRss(dt)

        let item = %*{
             "id": htmlUrl,
            "title": page.headers["title"],
            "url": htmlUrl,
            "content_text": page.content,
            "content_html": page.htmlContent
        }
        add(items, item)
    jsonfeed{"items"} = items

    var pout = open(filename, fmWrite)
    write(pout, pretty(jsonfeed))
    close(pout)


proc generateSitemap*() =
    var files: seq[string] = @[]
    let cd = getCurrentDir()
    let cdi = len(cd)+1
    for path in walkDirRec(cd):
        if endsWith(path, "-content.html") and not contains(path, "templates/"):
            let p = replace(path, "-content.html", DOT_HTML_EXT)
            add(files, p[cdi..len(p)-1])
    sort(files, system.cmp, SortOrder.Descending)

    let rootpage = loadRootPage(".")
    let url = rootpage.headers["url"]

    let tmps = loadTemplates(rootpage)
    let tmp = gettemplate(joinPath(template_dir_mappings[rootpage.dirname], "sitemap.xml"), true, tmps)

    repeat(tmp, "urls", len(files))

    var x = 0
    for file in files:
        setvalue(tmp, "url", file, indexOf(x))
        let mt = getLastModificationTime(replace(file, DOT_HTML_EXT, DOT_TEXT_EXT))
        setvalue(tmp, "lastmod", mt.format(DATE_FORMAT), indexOf(x))
        inc(x)

    writePage("sitemap.xml", tmp)