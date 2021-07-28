#!/usr/bin/env bash

pandoc ../README.md -s -H headInclude.html -o index.html -c docs.css -f markdown --metadata pagetitle="BWProxy"
