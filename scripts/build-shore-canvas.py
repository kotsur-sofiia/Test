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
    f'<symbol id="treasure-{i}" viewBox="{i % 4 * 250} {i // 4 * 250} 250 250">'
    '<use href="#treasure-atlas"/></symbol>' for i in range(8)
)
placements = [(0, '7%', 120, 33), (1, '84%', 310, 35),
              (2, '9%', 530, 26), (3, '81%', 720, 36),
              (4, '6%', 940, 36), (5, '85%', 1150, 29),
              (6, '10%', 1370, 28), (7, '80%', 1510, 34)]
treasures = '\n'.join(
    f'<use href="#treasure-{i}" x="{x}" y="{y}" width="{size}" height="{size}"/>'
    for i, x, y, size in placements
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
<image id="treasure-atlas" href="{details}" width="1000" height="500"/>
{symbols}
<pattern id="sand-treasures" patternUnits="userSpaceOnUse" width="100%" height="1680">
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
