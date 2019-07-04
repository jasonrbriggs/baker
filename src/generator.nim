import algorithm
import lists
import math
import os
import sequtils
import strformat
import strtabs
import strutils
import tables
import times

import markdown
import proton

import config
import pages
import utils

var template_dir_mappings = newStringTable()
var template_mappings = tables.initTable[string,Table[string,Template]]()


proc renderPage(page:Page) =
    let html = markdown(page.content)

    echo html


proc generateAll*(force:bool) =
    echo fmt"here {force}"


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
        setattribute(tmp, "post-date-time", "datetime", page.headers["posted-time"])
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
            setattribute(tmp, "taglink", "href", "/tags/" & tags[i] & ".html", indexof(i))
    else:
        hide(tmp, "taglinks")


proc generateContent(page:Page, tmps:Table[string,Template]):Template =
    let content_template = gettemplate(joinPath(template_dir_mappings[page.dirname], page.pageType & "-content.html"), true, tmps)
    setValueFromHeader(content_template, page, "title", "title")
    let html = markdown(page.content)
    setvalue(content_template, "content", html)
    setPostedTime(content_template, page)
    setTagLinks(content_template, page)
    setattribute(content_template, "permalink-url", "href", "/" & page.outputName)
    return content_template


proc generatePage(page:Page, tmps:Table[string,Template]):Template =
    # head setup
    let head_template = gettemplate(joinPath(template_dir_mappings[page.dirname], "head.html"), true, tmps)
    setValueFromHeader(head_template, page, "title", "title")
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

    # page setup
    let page_template = gettemplate(joinPath(template_dir_mappings[page.dirname], page.pageType & ".html"), true, tmps)
    setBannerImage(page_template, page)
    replace(page_template, "head", head_template)
    replace(page_template, "header", header_template)
    replace(page_template, "footer", foot_template)

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
    let prev = replace(name, ".html", prev_page & ".html")
    let next_num = page_num + 1
    let next = replace(name, ".html", "-" & next_num.`$` & ".html")
    if page_num == 0:
        if next_num < total:
            return ("", next)
        else:
            return ("", "")
    elif next_num >= total:
        return (prev, "")
    else:
        return (prev, next)


proc writeIndexPage(name:string, tmp:Template, page_num:int, total_pages:int) =
    let (prev, next) = getPrevNextPage(name, page_num, total_pages)
    setattribute(tmp, "prevpage", "href", "/" & prev)
    setattribute(tmp, "nextpage", "href", "/" & next)

    if page_num > 0:
        writePage(replace(name, ".html", "-" & page_num.`$` & ".html"), tmp)
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

    var cout = open(replace(page.outputName, ".html", "-content.html"), fmWrite)
    print(cout, content_template)
    close(cout)

    writePage(page.outputName, page_template)


proc generateIndexes*(directory:string, postsPerPage:int) =
    var files: seq[string] = @[]
    for path in walkDirRec(directory):
        if contains(path, "-content.html"):
            add(files, path)
    sort(files, system.cmp, SortOrder.Descending)

    var page = loadPage(directory, joinPath(directory, "index.text"))
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
