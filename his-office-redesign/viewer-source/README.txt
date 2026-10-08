HIS OFFICE — NEW DESIGN VIEWER

Open his-office-viewer.html in a recent browser with WebGL enabled.
That file embeds its models and libraries and makes no network requests.
This viewer contains only the new His Office design and its office shell.

Source version: run python3 serve.py, then open http://127.0.0.1:8770.
No installation is needed to run the source viewer; libraries are vendored.

Whole room gives an orbit view. Drag to rotate, scroll to zoom, and use
right-drag to pan. The cutaway clips architecture only; furniture stays whole.
The backs of wall art disappear when viewed through a removed near wall.
The four viewpoint shortcuts open eye-level walk views. Click the room to
look; W A S D or arrows move, Shift is faster, and Esc releases the mouse.
On touch devices, drag to look and use the on-screen arrow pad to move.
The menu button opens room controls during walking. Save image exports a PNG.

The 42 × 30 inch desktop is user-confirmed. Models use product dimensions
and available product assets; some shapes and fine profiles are simplified.
The cat stand base has a listed 23.6 × 22 inch
footprint; the reach of projecting branches remains an approximation.
The architectural shell follows the scan with reconstructed missing surfaces.
Recorded doors are closed by default. Hiding their leaves is a viewing aid
and marks an inferred open state; the measured openings do not change.
The closet interior was not scanned. Provisional shoe racks appear only
with door leaves hidden; their fit needs an on-site check.

All models retain native GLTF Y-up coordinates in metres, without rescaling.
assets/config.json contains exact camera poses and room metadata.
Rebuild the standalone file after updates with npm install and npm run build.
Three.js and three-mesh-bvh licences are included in vendor/.
