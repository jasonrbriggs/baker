import os
import streams
import strformat

import utils


proc writeFileContent(dir:string, name:string, content:string) =
    if not dirExists(dir):
        createDir(dir)

    let fname = joinPath(dir, name)
    var fs = newFileStream(fname, fmWrite)
    fs.write(content)
    fs.close()


proc initialise*(dir:string) =
    writeFileContent(dir, "Makefile", MAKEFILE)

    createDir(joinPath(dir, "css"))
    createDir(joinPath(dir, "img"))
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
    writeFileContent(templateDir, "micro-page-content.html", TEMPLATE_MICROPOSTCONTENT)
    writeFileContent(templateDir, "micro-post.html", TEMPLATE_MICROPOST)
    writeFileContent(templateDir, "page-content.html", TEMPLATE_PAGECONTENT)
    writeFileContent(templateDir, "page.html", TEMPLATE_PAGE)
    writeFileContent(templateDir, "post-content.html", TEMPLATE_POSTCONTENT)
    writeFileContent(templateDir, "post.html", TEMPLATE_POST)
    writeFileContent(templateDir, "tag.html", TEMPLATE_TAG)
    writeFileContent(templateDir, "tags.html", TEMPLATE_TAGS)

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

    writeFileContent(dir, "index.text", """title: [Site title here]
meta-description: [meta description goes here]
banner-image: /img/banner.jpg
url: http://example.org
type: page

""")