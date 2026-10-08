APARTMENT GEOMETRY AND REGISTRATION AUDIT

This audit uses actual world-space triangles from the original Polycam GLB imported into Blender scan.blend. It does not measure generated images.

Primary deliverables:
- geometry.json: common Z-up, meter coordinate system; measured room outlines, local elevations, landmarks, openings, stairs; explicit uncertainties and dimension disagreements.
- amy_scan_registration.png: Amy room fragments annotated against actual mesh geometry. This visibly checks rotation, handedness, wall and doorway correspondences.
- amy_affine_registration.json: separate schematic-to-world affine fits for upper rooms. Schematic dimensions do not override mesh dimensions.
- surface_plane_fits.json: robust local floor/ceiling plane fits with support areas and residuals, for intelligent patching.
- upstairs_wallmap.png and basement_wallmap.png: observed vertical surfaces at three heights, exposing real doors rather than treating every mesh gap as a door.
- mesh_summary.json and Mesh_N.npz: original world-space geometry evidence.

Confirmed axes: X toward front/street, -X toward backyard/rear; +Y toward bathroom/stair/white wall side; -Y toward long brick wall side; Z up. Listing page horizontal/right maps +Y and page downward maps +X. Amy uses the same rotation for the supplied fragments; do not mirror them.

Critical previous mistakes corrected:
1. His desk is against +Y wall near the -X rear end. It was previously assigned to +X wall opposite the exterior window/door without registration.
2. Her vanity and chest are against +Y wall. The former opposite-window/-X interpretation was incorrect.
3. Listing width/length must be swapped into world X/Y after rotating. The lower bedroom15ft11 by12ft5 means Y4.851m and X3.785m. Its irregular scan bounds4.60mY by4.00mX broadly agree; its smaller carved main rectangle is not the entire labeled room.
4. Upstairs bathroom door is on rear-facing X=-1.24 wall, Y≈0.52..1.35. Its living-facing Y≈0.39 wall is solid and can support a media console.
5. Basement dining table long axis runs across worldY, as the source table long edge follows imageU. Earlier table-along-room-X rule was wrong.
6. Basement king bed+nightstands must leave former bedroom/music door X=-3.8, Y≈-2.15..-1.35 clear. Curtain position is not dimensioned by Amy and may need to move toward +X to fit these real objects.

The old four-angle camera rectangles are insets chosen for renders, not room dimensions. Scan gaps and people artifacts made some views geometrically misleading. Furnishing should be placed once in measured3D coordinates, then every render generated from that same scene. More generative pictures alone cannot enforce room dimensions or consistency.

Confidence and limits:
- GLB encodes a metric scale and independent listing comparisons support retaining it.
- Mesh is slightly tilted/uneven; floor elevations differ several centimeters across rooms. Use local plane fits when bridging holes.
- Generalized room outlines have about0.05–0.12m positional uncertainty; scan not survey-grade.
- Upper front room scan width3.62m vs listing3.20m remains13% discrepancy. Do not silently stretch either source.
- Listing is explicitly illustrative with approximate dimensions. Amy drawing has no dimensions and room fragments are schematic with different scales.
- North is registered from listing arrow; geographic north was not surveyed in the scan.
- Unseen bathroom/laundry internals, doorway thresholds and upper stair landing are partly inferred; keep repair layer separate and visibly identifiable.
