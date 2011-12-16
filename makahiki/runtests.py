#!/usr/bin/env python

import os
import sys
import string

def main():
  """
  Executes the tests.  Requires the CherryPy live server to be installed.
  """
  command = "python manage.py test"
  # options = "--exe --with-selenium --with-selenium-fixtures --with-cherrypyliveserver"
  options = "--exe"
  apps = []
  if len(sys.argv) > 1:
    apps = sys.argv[1:]
    
  os.system(command + " " + string.join(apps, " ") + " " + options)

if __name__ == "__main__":
  main()