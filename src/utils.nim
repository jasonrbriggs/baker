import times
import json
import math
import re
import streams
import strutils
import tables
import times
import os


const
    Capitals:string = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    EmptyString*:string = ""


proc isEmpty*(s:string): bool =
    return s == EmptyString


proc findPathMatch*(path1, path2, originalPath2: string): string =
    var p1 = path1
    var p2 = path2
    if endsWith(p1, "/"):
        p1 = substr(p1, 0, len(p1)-2)
    if endsWith(p2, "/"):
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
    echo "here ;" & dir & ";"
    var d = dir
    if d == EmptyString:
        d = "."

    d = expandFilename(d)
    var filepath = joinPath(d, name)
    echo "...." & filepath
    if fileExists(filepath) or dirExists(filepath):
        return filepath
    elif isRootDir(d):
        echo "root dir..."
        return EmptyString

    let pardir = parentDir(d)
    if pardir == "." or pardir == dir or pardir == "":
        return EmptyString

    return findFileUp(pardir, name)


proc getRootDir*(dir:string): string =
    let dotbaker = findFileUp(dir, ".baker")
    if dotbaker == EmptyString:
        raise newException(OSError, "Unable to find root dir for site")
    return parentDir(dotbaker)


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


proc joinUrl*(s1:string, s2:string): string =
    var s2a = s2
    if startsWith(s2a, "/"):
        s2a = substr(s2a, 1)
    if endsWith(s1, "/"):
        return s1 & s2a
    else:
        return s1 & "/" & s2a


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
    if match(s, re"^.*\:[0-9]{2}"):
        d = s[0..len(s)-3] & ":" & s[len(s)-2..len(s)-1]
    return parse(d, "yyyy-MM-dd\'T\'HH:mm:sszzz", utc())


proc shortHash*(s:string):float64 =
    var i = 0
    for c in s:
        i += ord(c)
        echo "c = " & c & " = " & ord(c).`$`
    var s2 = i.`$`
    var i2 = 0
    echo "s2 = " & s2
    for c in s2:
        i2 += (ord(c) - 48)
    echo i2.`$`
    return float64(i2) / 30.0