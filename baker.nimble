# Package

version       = "2.0.9"
author        = "Jason R Briggs"
description   = "Static website generation"
license       = "Apache-2.0"
srcDir        = "src"
bin           = @["baker"]



# Dependencies

requires "nim >= 1.0.0"
requires "proton >= 0.2.4"
requires "docopt >= 0.6.8"
requires "markdown >= 0.8.0"
requires "zip >= 0.2.1"
requires "timezones >= 0.5.3"
requires "ndb >= 0.19.4"
