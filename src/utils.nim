import times
import json
import math
import re
import streams
import strutils
import tables
import times
import timezones
import os


const
    Capitals:string = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    EmptyString*:string = ""
    ForwardSlash*:string = "/"
    NEWLINE*:string = "\n"
    DATE_FORMAT*:string = "yyyy-MM-dd"
    DATETIME_FORMAT*:string = "yyyy-MM-dd\'T\'HH:mm:sszzz"
    RSS_PUBDATE_FORMAT*:string = "ddd, dd MMM yyyy HH:mm:ss zzz"
    ALL_CHARACTERS* = "0123456789ABCDEFGHJKLMNPQRSTUVWXYZ_abcdefghijkmnopqrstuvwxyz"
    MAKEFILE* = staticRead("resources/Makefile")


var numbers = initTable[char, int]()
var i = 0
for x in ALL_CHARACTERS:
    numbers[x] = i
    i += 1

numbers['l'] = 1 # typo lowercase l to 1
numbers['I'] = 1 # typo capital I to 1
numbers['O'] = 0 # typo capital O to 0

let baseTimezone:TimeZone = tz"Europe/London"
let urlDatePattern = re"[0-9]{4}/[0-9]{2}/[0-9]{2}"


proc isEmpty*(s:string): bool =
    return s == EmptyString


proc findPathMatch*(path1, path2, originalPath2: string): string =
    var p1 = path1
    var p2 = path2
    if endsWith(p1, ForwardSlash):
        p1 = substr(p1, 0, len(p1)-2)
    if endsWith(p2, ForwardSlash):
        p2 = substr(p2, 0, len(p2)-2)
    if endsWith(p1, p2):
        return substr(originalPath2, len(p2) + 1)
    var pos = rfind(p2, DirSep)
    if pos >= 0:
        p2 = substr(p2, 0, pos)
        if not isEmpty(p2):
            return findPathMatch(p1, p2, originalPath2)
    return originalPath2


proc findFileUp*(dir:string, name:string): string =
    var d = dir
    if d == EmptyString:
        d = "."

    d = expandFilename(d)
    var filepath = joinPath(d, name)
    if fileExists(filepath) or dirExists(filepath):
        return filepath
    elif isRootDir(d):
        return EmptyString

    let pardir = parentDir(d)
    if pardir == "." or pardir == dir or pardir == EmptyString:
        return EmptyString

    return findFileUp(pardir, name)


proc getRootDir*(dir:string): string =
    let makefile = findFileUp(dir, "Makefile")
    if makefile == EmptyString:
        raise newException(OSError, "Unable to find root dir for site")
    return parentDir(makefile)


iterator findFilesStartingWith*(dir:string, name:string): string =
    for kind, path in walkDir(dir):
        if kind == pcFile:
            var (_, filename, ext) = splitFile(path)
            if startsWith(filename, name):
                var f = joinPath(dir, filename & ext)
                yield f


proc defaultIfEmpty*(s:string, def:string): string =
    if isEmpty(s):
        return def
    return s


proc joinUrlPaths*(ps: varargs[string]): string =
    var paths:seq[string] = @[]
    for p in ps:
        if startsWith(p, ForwardSlash) and endsWith(p, ForwardSlash):
            add(paths, substr(p, 1, len(p)-1))
        elif startsWith(p, ForwardSlash):
            add(paths, substr(p, 1))
        elif endsWith(p, ForwardSlash):
            add(paths, substr(p, 0, len(p)-1))
        else:
            add(paths, p)
    return join(paths, ForwardSlash)


proc loadJson*(filename:string): JsonNode =
    try:
        var s = readFile(filename)
        return parseJson(s)
    except:
        return %*{}


proc jsonContains*(node:JsonNode, val:string): bool =
    if node.kind != JArray:
        return false
    for child in items(node):
        if child.kind == JString and val == child.str:
            return true
    return false


proc getJsonNode*(node:JsonNode, ks: varargs[string]): JsonNode =
    var n = node
    for k in items(ks):
        if not hasKey(n, k):
            return nil
        n = n[k]
    return n


proc getJsonValue*(node:JsonNode, ks: varargs[string]): string =
    var n = getJsonNode(node, ks)
    if n == nil:
        return EmptyString
    if n.kind == JString:
        if isEmpty(n.str):
            return EmptyString
        return n.str
    else:
        return pretty(n)


proc internalSplitPathComponents(s:string, paths:var seq[string]) =
    var ht = splitPath(s)
    if ht[0] != EmptyString:
        internalSplitPathComponents(ht[0], paths)
    if ht[1] != EmptyString:
        add(paths, ht[1])


proc splitPathComponents*(s:string): seq[string] =
    var paths: seq[string] = @[]
    internalSplitPathComponents(s, paths)
    return paths


proc parseDateTime*(s:string):DateTime =
    var d = s
    if not match(s, re"^.*:[0-9]{2}$"):
        d = s[0..len(s)-3] & ":" & s[len(s)-2..len(s)-1]
    return d.parse(DATETIME_FORMAT, baseTimezone)


proc formatDateTimeRss*(dt:DateTime):string =
    let ds = dt.format(RSS_PUBDATE_FORMAT)
    let pos = ds.rfind(":")-1
    return ds[0..pos] & ds[pos+2..len(ds)-1]


proc formatDateTime*(dt:DateTime):string =
    return dt.format(DATETIME_FORMAT)


proc shortHash*(s:string):float64 =
    var i = 0
    for c in s:
        i += ord(c)
    var s2 = i.`$`
    var i2 = 0
    for c in s2:
        i2 += (ord(c) - 48)
    return float64(i2) / 30.0

#   RewriteRule ^u/jbMdB6g$ /journal/2018/05/09/a-question-about-tkinter-update.html [R=301,L]
    # end of rewrite rules for short links

proc numtosxg*(n:int64):string =
    var s = ""
    var n0 = n
    var n1 = n
    while n1 > 0:
        n1 = n0 div 60
        var i = cast[int](n0 mod 60)
        n0 = n1
        s = ALL_CHARACTERS[i] & s
    return s


proc sxgtonum*(s:string):int =
    var n = 0
    for c in s:
        n = n * 60 + getOrDefault(numbers, c)
    return n


proc dateasnum*(url:string):int =
    var (first, last) = findBounds(url, urlDatePattern)
    if first < 0:
        return 0
    var date = substr(url, first, last)
    date = replace(date, "/", "")
    return parseInt(date)