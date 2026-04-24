# GITPUSH_INFO_VERSION=3.5
# Static site, no build. Sync root version into en/index.html after sitebump.
VER=$(grep -oP '<span class="version">v\K[0-9.]+' index.html | head -1)
if [[ -n "$VER" ]]; then
  sed -i "s|<span class=\"version\">v[0-9.]*</span>|<span class=\"version\">v${VER}</span>|" en/index.html
fi
