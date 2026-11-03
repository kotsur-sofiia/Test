"""Build the self-contained, responsive beach canvas used directly by the static app."""
from base64 import b64encode
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'


def image(name):
    return 'data:image/webp;base64,' + b64encode((ASSETS / name).read_bytes()).decode()


phone = image('shore-phone.webp')
desktop = image('shore-desktop.webp')
details = image('shore-details.webp')
symbols = '\n'.join(
    f'<symbol id="treasure-{i}" viewBox="{i % 4 * 300 + 3} {i // 4 * 300 + 3} 294 294">'
    '<use href="#treasure-atlas"/></symbol>' for i in range(8)
)
placements = [(0, '7%', 140, 28, -28), (1, '77%', 520, 25, 31),
              (2, '24%', 890, 14, -12), (3, '81%', 1225, 32, -37),
              (4, '17%', 1580, 28, 20), (5, '65%', 1840, 21, 54),
              (6, '4%', 2230, 27, -10), (7, '72%', 2500, 23, 13)]
treasures = '\n'.join(
    f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 300 300" overflow="visible" '
    f'opacity="{.72 if i in (3, 4) else 1}">'
    f'<g transform="rotate({angle} 150 150)"><use href="#treasure-{i}" width="300" height="300"/></g></svg>'
    for i, x, y, size, angle in placements
)

# No viewBox: geometry uses the actual paint viewport. Only the width controls the
# hero's scale; page height merely exposes more sand. All raster assets are embedded
# because SVGs loaded as CSS images cannot fetch external image dependencies.
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">
<style>
.coast {{ width:100%; height:300vw; }}
.coast-wide {{ display:none; }}
.sand-floor {{ fill:#eee7de; }}
@media(min-width:768px) {{ .coast-phone {{ display:none; }} .coast-wide {{ display:block; height:100vw; }} .sand-floor {{ fill:#ece2d8; }} }}
</style>
<defs>
<filter id="fine-grain" x="0" y="0" width="100%" height="100%">
<feTurbulence type="fractalNoise" baseFrequency=".78" numOctaves="3" seed="17" stitchTiles="stitch"/>
<feColorMatrix type="saturate" values="0"/>
</filter>
<pattern id="sand-grain" patternUnits="userSpaceOnUse" width="180" height="180">
<rect width="180" height="180" filter="url(#fine-grain)" opacity=".075"/>
</pattern>
<filter id="sand-relief" x="0" y="0" width="100%" height="100%">
<feTurbulence type="fractalNoise" baseFrequency=".012 .018" numOctaves="3" seed="29" stitchTiles="stitch"/>
<feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  .33 .33 .34 0 0"/>
<feDiffuseLighting surfaceScale="6" diffuseConstant="1" lighting-color="#fffaf0"><feDistantLight azimuth="225" elevation="55"/></feDiffuseLighting>
</filter>
<pattern id="sand-relief-tile" patternUnits="userSpaceOnUse" width="420" height="520">
<rect width="420" height="520" filter="url(#sand-relief)" opacity=".16"/>
</pattern>
<image id="treasure-atlas" href="{details}" width="1200" height="600"/>
{symbols}
<pattern id="sand-treasures" patternUnits="userSpaceOnUse" width="100%" height="2600">
{treasures}
</pattern>
<linearGradient id="sand-join" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="white"/><stop offset=".9" stop-color="white"/><stop offset="1" stop-color="black"/>
</linearGradient>
<mask id="join" maskUnits="objectBoundingBox" maskContentUnits="objectBoundingBox">
<rect width="1" height="1" fill="url(#sand-join)"/>
</mask>
</defs>
<rect class="sand-floor" width="100%" height="100%"/>
<rect width="100%" height="100%" fill="url(#sand-relief-tile)"/>
<rect width="100%" height="100%" fill="url(#sand-grain)"/>
<rect width="100%" height="100%" fill="url(#sand-treasures)"/>
<image class="coast coast-phone" href="{phone}" width="100%" height="1200" preserveAspectRatio="none" mask="url(#join)"/>
<image class="coast coast-wide" href="{desktop}" width="100%" height="1200" preserveAspectRatio="none" mask="url(#join)"/>
</svg>'''
(ASSETS / 'shore-canvas.svg').write_text(svg)
print('Built assets/shore-canvas.svg')
