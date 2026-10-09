# Apartment design studio

The complete apartment design work and the independent redesign of his office:
source scans and designer attachments, dimensioned models, walk-through viewers,
real product references, generated concepts, review documents, scripts and checks.
Earlier versions and generation attempts are retained as project history.

## Start with the latest office designs

- [His office: B/C design review and six matched images](his-office-pinterest/His-office-B-C-design-review.pdf)
- [His office: interactive 3D walkthrough and standing-desk control](his-office-pinterest/his-office-viewer.html)
- [B: editable charcoal/slat Blender model](his-office-pinterest/variants/b-charcoal-slat/model/his-office-design.blend)
- [C: editable navy Blender model](his-office-pinterest/variants/c-ink-studio/model/his-office-design.blend)
- [His office: measured furnished plan](his-office-pinterest/layout/final-furnished-plan.pdf)
- [His office: complete B/C delivery package](his-office-dark-designs.zip)

Both alternatives retain the white Honeywell 02E lamp, brown MUTTROS cat tree
and owned Mineral Herman Miller Aeron Size C. A Branch Tria electric standing
desk and a separate clear 140 × 60 cm project bench serve one person. Matching
display ledges, grouped artwork, a felt desk mat and a clothes-storage console
with an opal lamp and compact palm connect the workspace and visitor area.

B uses Peppercorn paint on the work and window walls with a bounded 3 × 2.4 m
Black Ash slat bay across both desks. C uses a smooth Naval paint wrap on the
same walls. White ceiling/trim and the existing brick remain. The proposed
furniture and accessories total $3,308.81 for B or $2,334.06 for C, excluding
paint, mounting, installation, tax and shipping. Owned items have no purchase
cost. Product research is dated October 8, 2026; no purchases were made.

The source models and measured plan control geometry. Three matching native
angles establish the room layout. Initial image generation used all three
angles and two original-product boards; camera corrections used the exact
target angle and those boards, and final refinements added the preceding
generator original. All 14 attempts are recorded. The six selected images
illustrate appearance and can vary details.
The model checks include full standing-desk travel, supports, the owned chair
and nominal 60 cm routing. Scan uncertainty is about 5–12 cm; confirm tight
fits, door operation, closet internals and mounting on site. Use full chair
pullback and clothes-drawer access sequentially.

## Apartment designs and earlier office version

- [His office: nine-page design review](his-office-redesign/His-office-design-review.pdf)
- [His office: offline 3D viewer](his-office-redesign/his-office-viewer.html)
- [His office: editable Blender model](his-office-redesign/model/his-office-design.blend)
- [His office: complete deliverable ZIP](his-office-redesign.zip)
- [Apartment: generated design review with Amy's boards](apartment-imagegen-v3/Amy-design-generated-images.pdf)
- [Apartment: offline 3D walk-through](apartment-walkthrough.html)
- [Apartment: editable integrated model](apartment-model/integrated.blend)

The earlier warm office proposal preserves the confirmed 42 × 30-inch Pheasantwood UPLIFT
desk, Honeywell 02E lamp and MUTTROS cat tree. It adds a separate second desk,
folded-clothes and office drawers, provisional closet shoe storage, a visitor
chair, rug and artwork. Its proposed new pieces total $2,344.43 before tax and
shipping at the October 8, 2026 research date.

The scan-based models and dimensioned plans control geometry and furniture
orientation. Generated images illustrate appearance. Tight fits, door swings,
closet internals, cat-tree reach and dresser wall fixing require field checks;
the delivered review documents record the practical limits and assumptions.

## View online with GitHub Pages

The hosted viewer hub is [Apartment design studio](https://btesser.github.io/apartment-design-studio/).
It provides the [whole-apartment viewer](https://btesser.github.io/apartment-design-studio/apartment-walkthrough/)
, the [latest B/C office viewer](https://btesser.github.io/apartment-design-studio/his-office-pinterest/viewer-source/),
and the [earlier office viewer](https://btesser.github.io/apartment-design-studio/his-office-redesign/viewer-source/).

To enable deployment, select **Settings → Pages → Build and deployment → Source → GitHub Actions**
in this repository. Push these changes to `main` (or run **Deploy viewers to GitHub Pages**
from the Actions tab). After the workflow succeeds, the links above will be live.
The workflow follows [GitHub's custom Pages workflow](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

The build downloads only the viewers' Git LFS models and publishes the landing page,
viewer code, vendored libraries and configured models to `_site/`.
It fails if models are missing or still LFS pointers. Models and textures load from
the same site; no CDN, Node install or application server is required.
The original standalone HTML paths redirect to the hosted viewers on Pages;
the archived offline HTML files remain available in the repository.

To build and check the deployment locally with Python 3 and Git LFS:

```sh
git lfs pull --include="apartment-walkthrough/assets/**,his-office-redesign/viewer-source/assets/**,his-office-pinterest/viewer-source/assets/**" --exclude=""
python3 scripts/test-pages.py
python3 scripts/build-pages.py
python3 -m http.server 8000 --directory _site
```

Open `http://localhost:8000/`. All links and viewer resources use relative paths,
so the site also works under the repository prefix used by GitHub Pages.

Optional browser smoke test (Node and the existing viewer's Playwright dependency):

```sh
npm install --prefix apartment-walkthrough
./apartment-walkthrough/node_modules/.bin/playwright install chromium
PLAYWRIGHT_MODULE=../apartment-walkthrough/node_modules/playwright/index.mjs node scripts/test-pages-browser.mjs
```

This serves `_site/` under `/apartment-design-studio/` and verifies all three viewers,
all 17 model layers, controls, legacy redirects and failed browser requests.
Set `CHROMIUM_PATH` to use an existing Chrome/Chromium installation.

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
- `his-office-pinterest/`: latest two dark office alternatives, matched native renders and generated studies, measured plans, real products, interactive viewer, source code and independent checks.
- `geometry-audit/`, `independent-qa/`, `apartment-review-checks/`, `design-fidelity/`: evidence and design checks.
- Root ZIP archives and helper scripts retain the delivered packages and their project history.

Dependency directories and runtime caches are excluded. Source code, dependency
manifests and all design artifacts are retained. `PROJECT-FILES.json` records the
original design artifacts included in the initial commit.
