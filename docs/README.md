# docs/

`index.html` is a self-contained single-page annotated view of all 40 trip
reports, ready to be served by GitHub Pages. No build step, no assets —
everything (CSS, JS, per-trip narratives, scene annotations) is inlined.

## Enable GitHub Pages

1. Go to the repo's **Settings → Pages**.
2. Under **Source**, select **Deploy from a branch**.
3. Pick **Branch: `main`** and **Folder: `/docs`**. Save.
4. After ~30 seconds, the site will be live at:
   `https://georgefejer91.github.io/The-phenomenology-of-hallucinogenic-experiences/`

## Regenerating

```sh
py 1.Recoding/scripts/14_build_github_pages_site.py
```

The generator reads from `1.Recoding/data/scenes.csv` + the per-trip
narratives in `1.Recoding/data/trips/`, so any change to the scene
taxonomy or driver classification propagates automatically next time the
script is run. Commit the regenerated `docs/index.html` to deploy.
