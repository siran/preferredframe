#!/usr/bin/env bash
set -e

# checkout main
git checkout main

for br in $(git branch | grep publish); do
    git branch -D "$br"
done

git clean -fdi
