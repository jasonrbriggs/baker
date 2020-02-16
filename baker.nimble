# Package

version       = "2.0.8"
author        = "Jason R Briggs"
description   = "Static website generation"
license       = "Apache-2.0"
srcDir        = "src"
bin           = @["baker"]



# Dependencies

requires "nim >= 1.0.0"
requires "proton >= 0.2.4"
requires "https://github.com/docopt/docopt.nim#head"
requires "markdown >= 0.2.0"
requires "zip >= 0.2.1"
requires "timezones >= 0.5.0"
requires "ndb >= 0.19.4"
