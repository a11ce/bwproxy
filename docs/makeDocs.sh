#!/usr/bin/env bash

pandoc ../README.md -s -o index.html -c docs.css -f markdown --metadata pagetitle="BWProxy"
