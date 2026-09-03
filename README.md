# Can I Share This?

Privacy-first static link and sender safety checker deployed on Vercel.

## Build

```bash
bash build.sh
```

The build reconstructs the static source, generates the product and editorial
pages, applies the central SEO route policy, then fails if it finds a broken
internal link, orphan page, duplicate metadata, duplicate intent, redirect
chain, non-canonical sitemap entry or unexpected generated route.

## SEO route governance

`seo/SEO_ROUTE_MANIFEST.json` is the only route authority. It declares every
active clean URL, canonical, cluster, role, search intent, primary keyword and
permanent redirect.

When changing a page:

1. Update its content generator.
2. Update the route registry if the URL, intent, cluster or canonical changes.
3. Add moved or merged URLs to `redirects` and mirror them in `vercel.json`.
4. Run `bash build.sh` and the Universal Safety Checker matrix.

The registry pass rewrites legacy internal links, removes duplicate HTML
outputs, adds compact cluster links and rebuilds `sitemap.xml` from canonical,
indexable routes only. GitHub Actions runs the same checks for pull requests and
every push to `main`.
