#!/usr/bin/env bash
set -euo pipefail

# 用法: ./scripts/install_open_url_launchd.sh "https://yourname.github.io/repo/"
URL="${1:-}"
if [[ -z "$URL" ]]; then
  echo "请传入GitHub Pages网址，例如:"
  echo "./scripts/install_open_url_launchd.sh https://yourname.github.io/quote-pages/"
  exit 1
fi

PLIST="$HOME/Library/LaunchAgents/com.chinacnu.dailyquote.openurl.plist"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.chinacnu.dailyquote.openurl</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/open</string>
    <string>$URL</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key><integer>9</integer>
    <key>Minute</key><integer>10</integer>
  </dict>
  <key>RunAtLoad</key><true/>
</dict>
</plist>
EOF

launchctl unload "$PLIST" >/dev/null 2>&1 || true
launchctl load "$PLIST"

echo "已安装：每天 09:10 自动打开 $URL"
