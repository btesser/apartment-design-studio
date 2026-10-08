HIS OFFICE PINTEREST REVISION — PREPARED MODEL WORKFLOW

This is a separate revision folder. No prior scene or image is overwritten.
The source is the corrected frozen His Office scene, SHA256
607e11d67b8fc8813da0872b5f18278733c6a40cd9e1988c3b1cb743971ada0a.
Native units remain meters, Blender Z-up; glTF maps (X,Z,-Y). No recentering,
room scaling, mirroring, keeper resizing or modified door/window dimensions.

The measured structure, fixed fixtures and observed closed door leaves are
geometry-protected. The three owned keeper forms and shader/texture assignments
are protected: UPLIFT42x30in, Honeywell open head/two narrow LED bars, MUTTROS tree.
A recipe can rigidly move or rotate a whole keeper, but cannot stretch its form.
All source images are already packed; do not repack them. New images are packed
only when not already packed and when they have a real filepath.

PREPARED FILES
scene-inventory.json contains14 product roots, two separate generic equipment
roots, active material users, two light templates and four cameras.
protected-geometry.json fingerprints fixed structure and keeper geometry/finish.
keeper-material-guard.json and its TXT summary independently document sharing.
revision-recipe.json is deliberately inactive while the new finish/product
selection is pending. clear-project-bench-option.json records the chosen
footprint direction: remove the second task chair and second monitor group,
move visitor chair20cm left, keep the140x60 bench envelope. It remains a dry run.

PIPELINE
inspect_scene.py opens the old scene read-only and writes inventory here.
build_revision.py -- --dry-run validates IDs, recipe and source protection.
Once the root provides final actual products/finishes, the recipe can remove
product hierarchies/equipment, rigidly reposition roots, privately copy selected
materials, update product metadata, and call a new dimensioned product builder.
A different-sized bench is rebuilt from chosen dimensions rather than stretching
an old CAD product. Equipment follows its associated desk during rigid moves.

The build writes his-office-pinterest-design.blend, a furniture-only GLB and a
composite GLB only in this folder. Existing source geometry and keeper finishes
are checked before export and again before completion. Source file hash must
remain unchanged. No new finished scene/export has been produced yet.

render_revision.py uses the chosen saved scene for four camera views, previews
and final source frames, then records lens/poses and unit conversion. Existing
camera positions must be checked against the final new layout before rendering.

RUNTIME
This machine has4 CPU cores available. Blender4.3.2 CPU Cycles has no supported
OpenImageDenoise option. Existing settings:1440x1000,64 adaptive samples,
threshold0.03/minimum16, AgX Medium High Contrast, exposure-0.5. Expect about
3.5–5 minutes per final view and about45 seconds per1000x694/24sample preview.
Two retained area lights: ceiling fill230W and window daylight260W. Geometry
and appearance are separate: generated finish concepts do not verify dimensions.
