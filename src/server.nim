import asynchttpserver, asyncdispatch
import mimetypes
import os
import strutils


let mimedb = newMimetypes()


proc handleMissingFile(req: Request, name: string): Future[void] =
    echo "Unable to find file: " & name
    return req.respond(Http404, "Not found")


proc handleGet(req: Request, name: string, ext:string): Future[void] =
    var filename = name
    var fileext = ext
    if dirExists(filename):
        filename = joinPath(filename, "index.html")
        fileext = "html"

    var headers = newHttpHeaders()

    if not fileExists(filename):
        return handleMissingFile(req, filename)

    var err:bool = false
    var content: string = ""
    try:
        content = readFile(filename)
    except:
        echo getCurrentExceptionMsg()
        err = true

    if err:
        return req.respond(Http500, "Unexpected server error")

    let mimetype = getMimetype(mimedb, fileext)
    add(headers, "Content-Type", mimetype)

    return req.respond(Http200, content, headers)


proc runServer*(dir:string = "", port:int) =
    echo "Starting server on port " & port.`$`

    var server = newAsyncHttpServer()

    proc cb(req: Request) {.async, gcsafe, closure.} =
        var name = joinPath(dir, req.url.path)
        # edge-case, don't think it can happen
        if not startsWith(name, dir):
            await req.respond(Http400, "Bad request, " & name & " not accessible")
            return

        var (dirname, filename, ext) = splitFile(name)

        var err: bool = false

        if req.reqMethod == HttpGet:
            await handleGet(req, name, ext)

        else:
            await req.respond(Http501, "Method not supported")

    waitFor server.serve(Port(port), cb)