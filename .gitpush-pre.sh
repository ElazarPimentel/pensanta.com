# GITPUSH_INFO_VERSION=3.5
#!/usr/bin/env bash
set -e

VER=$(grep -oP '<span class="version">v\K[0-9.]+' index.html)
sed -i "s|<span class=\"version\">v[0-9.]*</span>|<span class=\"version\">v${VER}</span>|" en/index.html
