# Apartment design archive

The complete apartment design work and the independent redesign of his office:
source scans and designer attachments, dimensioned models, walk-through viewers,
real product references, generated concepts, review documents, scripts and checks.
Earlier versions and generation attempts are retained as project history.

## Start with the completed designs

- [His office: nine-page design review](his-office-redesign/His-office-design-review.pdf)
- [His office: offline 3D viewer](his-office-redesign/his-office-viewer.html)
- [His office: editable Blender model](his-office-redesign/model/his-office-design.blend)
- [His office: complete deliverable ZIP](his-office-redesign.zip)
- [Apartment: generated design review with Amy's boards](apartment-imagegen-v3/Amy-design-generated-images.pdf)
- [Apartment: offline 3D walk-through](apartment-walkthrough.html)
- [Apartment: editable integrated model](apartment-model/integrated.blend)

The new office design preserves the confirmed 42 × 30-inch Pheasantwood UPLIFT
desk, Honeywell 02E lamp and MUTTROS cat tree. It adds a separate second desk,
folded-clothes and office drawers, provisional closet shoe storage, a visitor
chair, rug and artwork. Its proposed new pieces total $2,344.43 before tax and
shipping at the October 8, 2026 research date.

The scan-based models and dimensioned plans control geometry and furniture
orientation. Generated images illustrate appearance. Tight fits, door swings,
closet internals, cat-tree reach and dresser wall fixing require field checks;
the delivered review documents record the practical limits and assumptions.

## Get the actual model and image files

Large and binary design files use [Git LFS](https://git-lfs.com/). Install Git LFS
before cloning, then run:

```sh
git lfs install
git clone <private-repository-url>
cd <repository-folder>
git lfs pull
```

Download the standalone HTML viewers and open them in a desktop browser. Their
models and textures are embedded.

## Contents

- `apartment/`, `attachments/`, `source-evidence/`: original capture and design sources.
- `apartment-model/`, `apartment-furniture/`, `apartment-v2/`: apartment models, furniture, plans and deterministic renders.
- `apartment-walkthrough/`: maintainable whole-apartment viewer source and assets.
- `apartment-design/`, `apartment-imagegen-v3/`, `generated_images/`: reference views and generated design concepts, including earlier iterations.
- `his-office-redesign/`: final office proposal, model, viewer, products, image-generation references, and delivery copy.
- `geometry-audit/`, `independent-qa/`, `apartment-review-checks/`, `design-fidelity/`: evidence and design checks.
- Root ZIP archives and helper scripts retain the delivered packages and their project history.

Dependency directories and runtime caches are excluded. Source code, dependency
manifests and all design artifacts are retained. `PROJECT-FILES.json` records the
original design artifacts included in the initial commit.
