import options
import os
import strtabs
import strutils

import ndb/sqlite

import utils


proc openDatabase*(rootdir:string):DbConn =
    let db = open(joinPath(rootdir, "baker.db"), "", "", "")
    db.exec(sql"CREATE TABLE IF NOT EXISTS pages (url text, shorturl text, created_date text)")
    db.exec(sql"CREATE TABLE IF NOT EXISTS federated (url text, federated_to text, fed_date text)")

    try:
        db.exec(sql"ALTER TABLE pages ADD COLUMN created_date text")
    except:
        discard

    try:
        db.exec(sql"ALTER TABLE federated ADD COLUMN fed_date text")
    except:
        discard        

    return db

