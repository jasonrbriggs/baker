# Package

version       = "2.0.1"
author        = "Jason R Briggs"
description   = "Static website generation"
license       = "Apache-2.0"
srcDir        = "src"
bin           = @["baker"]



# Dependencies

requires "nim >= 0.20.0"
requires "proton >= 0.2.2"
requires "https://github.com/docopt/docopt.nim#head"
requires "markdown >= 0.2.0"
requires "zip >= 0.2.1"
requires "timezones >= 0.5.0"