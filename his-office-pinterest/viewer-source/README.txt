HIS OFFICE — B AND C DESIGN ALTERNATIVES

Open his-office-viewer.html in a recent browser with WebGL enabled.
That standalone file embeds both alternatives, their textures and libraries.
The room viewer makes no network requests and works without a server.
The accompanying variants folders contain the editable Blender models.

B: Charcoal + slat. C: Ink studio. Use Design alternative to switch.
Both alternatives use the same measured room and shared furniture layout.
Only the proposed wall treatment and room palette differ.

Whole room gives an orbit view: drag to rotate, scroll to zoom, right-drag
 to pan. The wall cutaway clips architecture only; furniture stays whole.
Wall-art backs disappear when a removed near wall would leave them in view.
Viewpoint shortcuts open the exact eye-level camera positions of the model.
Their horizontal lens field of view is preserved at any screen proportion.
Click the room to look; W A S D or arrows move, Shift is faster and Esc
releases the mouse. Touch users can drag to look and use the arrow pad.
The menu opens controls while walking. Save image exports the current view.

The furniture inspector lists actual item sizes and facing directions.
The Branch Tria primary worktop uses the official supplier CAD: 120 × 68.5
cm, height adjustable. Catalog dimensions are approximately 119.9 × 68.6 cm.
The second 140 × 60 cm work surface stays clear for projects. There is one
daily task chair and one visitor chair. The owned Honeywell floor lamp and
MUTTROS cat tree retain their modeled geometry and placement.

Models use available product dimensions and assets; fine shapes and finish
rendering are simplified. The cat tree base is listed at 23.6 × 22 inches;
its projecting branches remain provisional. The room shell follows the
scan with reconstructed missing surfaces and roughly 5–12 cm wall-position
uncertainty. Check physical fit, door swings and drawer access on site.

Doors match the recorded closed state by default. Hiding their leaves is
an inferred viewing aid, not a verified hinge/swing design. The measured
openings do not change. The closet interior was not scanned. Shoe racks
appear only with leaves hidden and require a physical closet-fit check.
Walking uses approximate collision checks; it is not an accessibility test.

All GLBs retain native GLTF Y-up coordinates in metres without rescaling.
The offline WebGL preview uses neutral lighting, not the exact Blender
render engine. assets/config.json seals model/camera/layout identities;
assets/source-hashes.json identifies the exact copied source GLBs.
The model download links require the accompanying variant folders. These
are included as sibling folders in the viewer source ZIP; extract them all.

Source viewer: run python3 serve.py then open http://127.0.0.1:8773.
No installation is needed to run the source viewer; libraries are vendored.
To rebuild after source model updates: python3 sync-assets.py, npm install,
then npm run build. Run npm test for a browser check of both alternatives.
Three.js and three-mesh-bvh licenses are included under vendor/.
