import os
import streams
import strformat

import utils


const
    TEMPLATE_FOOT = staticRead("resources/templates/foot.html")
    TEMPLATE_HEAD = staticRead("resources/templates/head.html")
    TEMPLATE_HEADER = staticRead("resources/templates/header.html")
    TEMPLATE_MICROPAGE = staticRead("resources/templates/micro-page.html")
    TEMPLATE_MICROPOSTCONTENT = staticRead("resources/templates/micro-post-content.html")
    TEMPLATE_MICROPOST = staticRead("resources/templates/micro-post.html")
    TEMPLATE_PAGECONTENT = staticRead("resources/templates/page-content.html")
    TEMPLATE_PAGE = staticRead("resources/templates/page.html")
    TEMPLATE_POSTCONTENT = staticRead("resources/templates/post-content.html")
    TEMPLATE_POST = staticRead("resources/templates/post.html")
    TEMPLATE_RSS = staticRead("resources/templates/rss.xml")
    TEMPLATE_SITEMAP = staticRead("resources/templates/sitemap.xml")
    TEMPLATE_TAG = staticRead("resources/templates/tag.html")
    TEMPLATE_TAGS = staticRead("resources/templates/tags.html")
    GRAVATAR_IMAGE = staticRead("resources/gravatar.png")


proc writeFileContent(dir:string, name:string, content:string) =
    if not dirExists(dir):
        createDir(dir)

    let fname = joinPath(dir, name)
    var fs = newFileStream(fname, fmWrite)
    fs.write(content)
    fs.close()


proc initialise*(dir:string) =
    writeFileContent(dir, "Makefile", MAKEFILE)

    let cssDir = joinPath(dir, "css")
    createDir(cssDir)
    let imgDir = joinPath(dir, "img") 
    createDir(imgDir)
    createDir(joinPath(dir, "js"))
    createDir(joinPath(dir, "tags"))
    createDir(joinPath(dir, "css"))
    let blogDir = joinPath(dir, "blog")
    createDir(blogDir)
    let microDir = joinPath(dir, "micro") 
    createDir(microDir)

    let templateDir = joinPath(dir, "templates")
    writeFileContent(templateDir, "foot.html", TEMPLATE_FOOT)
    writeFileContent(templateDir, "head.html", TEMPLATE_HEAD)
    writeFileContent(templateDir, "header.html", TEMPLATE_HEADER)
    writeFileContent(templateDir, "micro-page.html", TEMPLATE_MICROPAGE)
    writeFileContent(templateDir, "micro-post-content.html", TEMPLATE_MICROPOSTCONTENT)
    writeFileContent(templateDir, "micro-post.html", TEMPLATE_MICROPOST)
    writeFileContent(templateDir, "page-content.html", TEMPLATE_PAGECONTENT)
    writeFileContent(templateDir, "page.html", TEMPLATE_PAGE)
    writeFileContent(templateDir, "post-content.html", TEMPLATE_POSTCONTENT)
    writeFileContent(templateDir, "post.html", TEMPLATE_POST)
    writeFileContent(templateDir, "rss.xml", TEMPLATE_RSS)
    writeFileContent(templateDir, "sitemap.xml", TEMPLATE_SITEMAP)
    writeFileContent(templateDir, "tag.html", TEMPLATE_TAG)
    writeFileContent(templateDir, "tags.html", TEMPLATE_TAGS)

    writeFileContent(imgDir, "gravatar.png", GRAVATAR_IMAGE)

    let now = getCurrentDateTime()
    let postedTime = formatDateTime(now)
    writeFileContent(microDir, "index-page.text", fmt"""title: [Microblog title]
posted-time: {postedTime}
type: micro-post
url: http://example.org/micro
description: [Microblog feed description]
tags: 

""")

    writeFileContent(blogDir, "index-page.text", fmt"""title: [Blog title]
posted-time: {postedTime}
tags: 
url: http://example.org/blog
description: [Blog description]

""")

    writeFileContent(dir, "index.text", fmt"""title: [Site title here]
posted-time: {postedTime}
meta-description: [meta description goes here]
banner-image: /img/banner.jpg
url: http://example.org
type: page

""")

    writeFileContent(cssDir, "stylesheet.css", """
.avatar img {
width:48px;
height:48px;
display:inline-block;
vertical-align:top;
padding-top:5px;
padding-right:6px;
float:left;
}
""")