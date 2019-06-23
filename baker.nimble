# Package

version       = "0.1.0"
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