APARTMENT WALKTHROUGH

The standalone apartment-walkthrough.html opens by double-clicking. It embeds
the original scan, inferred gap repairs and furniture layout and makes no
network requests. Use a recent browser with WebGL enabled.

For the maintainable source viewer in this folder:
  python3 serve.py
Then open http://127.0.0.1:8765 in a recent browser. Keep the terminal open.
No installation is required; Three.js and its helper libraries are included.

CONTROLS
Orbit: drag to rotate, scroll to zoom, right-drag to pan.
Walk: click Walk, then click the 3D view. Move with W A S D or arrow keys,
hold Shift to move faster, and press Esc to release the mouse.
Touch: drag to look and use the arrow pad to move.
Floor and room menus move you to defined views. The plan shows your position.
In orbit mode, the wall-cutaway slider reveals furniture without changing the
underlying mesh. Save view downloads the current 3D view as a PNG.

INSPECT THE EVIDENCE
Recorded scan is the unscaled original Polycam geometry.
Filled gaps is a separate inferred repair layer, which can be highlighted.
Measured shell is a reconstruction of observed room outlines and openings;
local wall and ceiling heights remain tied to the source scan. Existing
fixtures are dimensioned proxies from observed scan locations.
Furniture layout uses spatially placed dimensional proxy models. It is a
layout review, not a representation of exact product detailing.
The proposed dresser is included by default. Its approximately 0.47 m bed
foot clearance is displayed; the dresser-off toggle is a comparison only.
Optional utility outlines are listing-only inferences. Those interiors were
not recorded, and that optional layer is off initially.
The separate entry design layer is on initially, with provisional placement
clearly stated. Amy selected those products but did not supply their positions.
All model layers share original GLTF Y-up coordinates in metres. The model
was not stretched to match a design board or an image-generator picture.
Repairs and tentative furniture are approximations and require confirmation
against the apartment before construction or furniture purchasing.

TO REBUILD THE STANDALONE HTML AFTER CHANGING ASSETS
  npm install
  node build-standalone.mjs
Node is required only for rebuilding, not for opening the supplied viewer.

See assets/config.json for room camera poses, bounds and the model sources.
Three.js and three-mesh-bvh licences are in vendor/.
