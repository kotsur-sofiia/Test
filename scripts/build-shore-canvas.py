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
    f'<symbol id="treasure-{i}" viewBox="{i % 4 * 300} {i // 4 * 300} 300 300">'
    '<use href="#treasure-atlas"/></symbol>' for i in range(12)
)
placements = [(0, '4%', 85, 34, -12), (7, '78%', 160, 19, 15),
              (10, '85%', 310, 34, -23), (5, '10%', 440, 38, 28),
              (4, '82%', 565, 17, -18), (2, '6%', 625, 23, 9),
              (3, '76%', 790, 36, 33), (6, '87%', 925, 30, -25),
              (9, '12%', 1030, 20, 42), (1, '5%', 1190, 32, 16),
              (7, '84%', 1315, 17, -11), (11, '9%', 1455, 26, 27),
              (8, '79%', 1580, 29, -19), (2, '14%', 1710, 21, -7),
              (5, '5%', 1860, 35, -30), (0, '85%', 1990, 28, 39),
              (4, '10%', 2135, 15, -16), (6, '76%', 2260, 33, 21)]
treasures = '\n'.join(
    f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 300 300" overflow="visible" '
    f'opacity="{.72 if i in (5, 6) else 1}">'
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
@media(min-width:768px) {{ .coast-phone {{ display:none; }} .coast-wide {{ display:block; height:100vw; }} }}
</style>
<defs>
<filter id="fine-grain" x="0" y="0" width="100%" height="100%">
<feTurbulence type="fractalNoise" baseFrequency=".78" numOctaves="3" seed="17" stitchTiles="stitch"/>
<feColorMatrix type="saturate" values="0"/>
</filter>
<pattern id="sand-grain" patternUnits="userSpaceOnUse" width="180" height="180">
<rect width="180" height="180" filter="url(#fine-grain)" opacity=".055"/>
</pattern>
<image id="treasure-atlas" href="{details}" width="1200" height="900"/>
{symbols}
<pattern id="sand-treasures" patternUnits="userSpaceOnUse" width="100%" height="2400">
{treasures}
</pattern>
<linearGradient id="sand-join" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="white"/><stop offset=".9" stop-color="white"/><stop offset="1" stop-color="black"/>
</linearGradient>
<mask id="join" maskUnits="objectBoundingBox" maskContentUnits="objectBoundingBox">
<rect width="1" height="1" fill="url(#sand-join)"/>
</mask>
</defs>
<rect width="100%" height="100%" fill="#efd8b9"/>
<rect width="100%" height="100%" fill="url(#sand-grain)"/>
<rect width="100%" height="100%" fill="url(#sand-treasures)"/>
<image class="coast coast-phone" href="{phone}" width="100%" height="1200" preserveAspectRatio="none" mask="url(#join)"/>
<image class="coast coast-wide" href="{desktop}" width="100%" height="1200" preserveAspectRatio="none" mask="url(#join)"/>
</svg>'''
(ASSETS / 'shore-canvas.svg').write_text(svg)
print('Built assets/shore-canvas.svg')
