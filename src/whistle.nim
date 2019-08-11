import os
import strutils

import pages
import utils

const
    HTACCESS_SHORTLINK_END_COMMENT = "# end of rewrite rules for short links"


proc ftype(fname:string):string =
    var (_, _, e) = splitFile(fname)
    var ext = toLowerAscii(e)
    if ext == ".html" or ext == ".htm":
        return "b"
    elif ext == ".text" or ext == ".txt":
        return "t"
    elif ext == ".png" or ext == ".gif" or ext == ".jpg" or ext == ".jpeg":
        return "p"
    return EmptyString


proc addShortenedUrl*(rootdir:string, page:var Page) =
    let path = page.outputName
    var dirpath = substr(path, 0, rfind(path, "/"))
    var filename = substr(path, rfind(path, "/") + 1)

    if dirpath == EmptyString:
        return

    var date = dateasnum(dirpath)
    if date == 0:
        return

    let firstchar = substr(path, 1, 1)
    let ft = ftype(filename)

    if ft == EmptyString:
        return

    var x = 0
    for (k,f) in walkDir(dirpath):
        inc(x)
        if f == path:
            break
    
    let sxg = numtosxg(((date - 19900101) * 1000) + x)

    let shortlink = "u/" & firstchar & ft & sxg
    let matchpattern = "^" & shortlink & "$" 
    let rule = "RewriteRule " & matchpattern & " /" & page.outputName & " [R=301,L]"

    let htaccess = joinPath(rootdir, ".htaccess")
    if not existsFile(htaccess):
        return
    let s = readFile(htaccess)
    if find(s, HTACCESS_SHORTLINK_END_COMMENT) < 0:
        return
    
    if find(s, matchpattern) < 0: 
        let replacement = rule & "\n\t" & HTACCESS_SHORTLINK_END_COMMENT
        let newhtaccess = replace(s, HTACCESS_SHORTLINK_END_COMMENT, replacement)
        var pout = open(htaccess, fmWrite)
        write(pout, newhtaccess)
        close(pout)

    page.shortLink = shortlink