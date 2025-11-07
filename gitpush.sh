#!/bin/bash

# Git push script
# Adds all changes, commits with a message, and pushes to remote

git add .
git commit -m "${1:-Update files}"
git push

