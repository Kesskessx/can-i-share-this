'use strict';

const fs = require('fs');
const path = require('path');

const regularFont = require.resolve('dejavu-fonts-ttf/ttf/DejaVuSans.ttf');
const boldFont = require.resolve('dejavu-fonts-ttf/ttf/DejaVuSans-Bold.ttf');
const fontDir = path.dirname(regularFont);
const configDir = path.join('/tmp', 'cist-fontconfig');
const configFile = path.join(configDir, 'fonts.conf');

fs.mkdirSync(configDir, { recursive: true });

if (!fs.existsSync(configFile)) {
  const escapedFontDir = fontDir
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  fs.writeFileSync(configFile, `<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <dir>${escapedFontDir}</dir>
  <cachedir>/tmp/fonts-cache</cachedir>
  <alias><family>Arial</family><prefer><family>DejaVu Sans</family></prefer></alias>
  <alias><family>Helvetica</family><prefer><family>DejaVu Sans</family></prefer></alias>
  <alias><family>sans-serif</family><prefer><family>DejaVu Sans</family></prefer></alias>
  <config></config>
</fontconfig>
`);
}

process.env.FONTCONFIG_PATH = configDir;
process.env.FONTCONFIG_FILE = 'fonts.conf';

module.exports = { regularFont, boldFont, fontDir };
