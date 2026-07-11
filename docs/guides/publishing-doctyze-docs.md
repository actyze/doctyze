---
doctyze:
  artifact: guide
  last_verified: 2026-07-11
---

# Guide — Publishing your Doctyze docs

Doctyze writes plain Markdown into `docs/`. It does **not** ship a website, and
deliberately won't — hosting, search, and theming are already solved by mature
tools ([ADR-0003](../architecture/decisions/0003-pivot-to-context-layer-generator.md);
[ROADMAP → non-goals](https://github.com/actyze/doctyze/blob/main/ROADMAP.md)).

So if you want a searchable, themed site, you don't need anything from us but a
config file — and writing one from scratch (theme, search, Mermaid, nav) is the
annoying part. This guide gives you that config, ready to paste, for whichever
generator you already run. **Your Markdown stays untouched.**

## Which one?

| | **MkDocs-Material** | **Backstage TechDocs** | **Docusaurus** |
|---|---|---|---|
| Setup | copy one file | one file + catalog entry | a Node project |
| Search / theming | built in | built in | built in |
| Mermaid diagrams | yes | yes | yes |
| Pick it when | you want the lightest path | you're already on Backstage | you're already on Docusaurus / want React |

**Start with MkDocs-Material** — it's the lightest, and it's the same engine
Backstage TechDocs runs on, so the one config below covers two of the three.

---

## MkDocs-Material

Save this as `mkdocs.yml` at your repo root (beside `docs/`) and change
`site_name`:

```yaml
site_name: Your Project            # change to your repo's name
site_description: Docs generated and kept fresh by Doctyze.
docs_dir: docs

theme:
  name: material
  features:
    - navigation.instant
    - navigation.tracking
    - navigation.top
    - navigation.indexes     # each folder's index.md becomes its section landing page
    - toc.follow
    - content.code.copy
    - search.suggest
    - search.highlight
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      toggle: { icon: material/weather-night, name: Switch to dark mode }
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      toggle: { icon: material/weather-sunny, name: Switch to light mode }

# Nav is intentionally omitted so it auto-builds from the docs/ tree — Doctyze
# gives every folder an index.md, and navigation.indexes turns each into a
# section landing page. Nothing to hand-maintain as docs are added or removed.

markdown_extensions:
  - admonition
  - toc: { permalink: true }
  - pymdownx.superfences:      # renders Doctyze's Mermaid diagrams
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.highlight
  - pymdownx.details
  - tables

plugins:
  - search

extra_javascript:
  - https://unpkg.com/mermaid@11/dist/mermaid.min.js
```

Then:

```bash
pip install mkdocs-material
mkdocs serve            # live preview at http://127.0.0.1:8000
mkdocs gh-deploy        # publish to GitHub Pages (or `mkdocs build` for ./site)
```

---

## Backstage TechDocs

TechDocs is MkDocs under the hood, so reuse the `mkdocs.yml` above with one
change — swap its `plugins:` block for `techdocs-core`, which bundles the
admonition/table/Mermaid extensions:

```yaml
plugins:
  - techdocs-core
```

Then add a `catalog-info.yml` at your repo root and register it in Backstage:

```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: your-project
  description: Docs generated and kept fresh by Doctyze.
  annotations:
    backstage.io/techdocs-ref: dir:.   # build from this repo using mkdocs.yml
spec:
  type: service
  lifecycle: production
  owner: your-team                     # your Backstage group/user
```

Backstage renders the `docs/` tree under the component's **Docs** tab. Mermaid
diagrams render via `techdocs-core` — no extra plugin.

---

## Docusaurus

Docusaurus needs its own Node project, but still consumes `docs/` as-is:

```bash
npx create-docusaurus@latest site classic
# delete the scaffolded site/docs and site/blog, then paste the two files below
cd site && npm install @docusaurus/theme-mermaid && npm run start
```

`site/docusaurus.config.js` — point `docs.path` at your repo's `docs/` and set
`url`:

```js
// @ts-check
/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Your Project',
  url: 'https://your-org.github.io',
  baseUrl: '/',
  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',
  presets: [
    ['classic', /** @type {import('@docusaurus/preset-classic').Options} */ ({
      docs: {
        path: '../docs',           // your repo's Doctyze docs/ tree; adjust to your layout
        routeBasePath: '/',        // docs-only mode: serve docs at the site root
        sidebarPath: require.resolve('./sidebars.js'),
      },
      blog: false,
    })],
  ],
  markdown: { mermaid: true },     // renders Doctyze's Mermaid diagrams
  themes: ['@docusaurus/theme-mermaid'],
  themeConfig: {
    navbar: { title: 'Your Project', items: [{ to: '/', label: 'Docs', position: 'left' }] },
    colorMode: { respectPrefersColorScheme: true },
  },
};
module.exports = config;
```

`site/sidebars.js` — autogenerated from the tree, so nothing is hand-listed:

```js
// @ts-check
/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
module.exports = {
  docs: [{ type: 'autogenerated', dirName: '.' }],
};
```

---

## The one rule

Whichever you pick: **don't edit the generated Markdown to make it render.**
Every config above consumes Doctyze's output untouched, so `doctyze` can keep
regenerating and freshness-checking `docs/` without fighting your site build.
