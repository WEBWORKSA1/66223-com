# 66223.com

Independent living, relocation & home-money guide for ZIP 66223 (south Overland Park, Kansas). Static HTML/CSS/JS, hosted free on GitHub Pages.

- **40 indexable pages**: home, 14 guides, 6 Kansas-specific calculators, multi-step lead funnel, data snapshot, videos, community, contests + official rules, donate, careers, advertise, list-your-business, about, contact, editorial policy, privacy, terms, disclaimer, sitemap.
- **Monetization**: Google AdSense (ca-pub-6620975821265271) in every page head + `ads.txt`; lead generation; sponsorships; donations.
- **Forms**: all forms post via FormSubmit AJAX to an address assembled at runtime — no email address appears in the HTML. The first submission triggers a one-time FormSubmit activation email; confirm it once.
- **Strategy + phase-wise build prompts**: see `BUILD-PROMPTS.md`.

## How it builds
GitHub Pages builds this repo with Jekyll automatically on every push — no Actions needed. Pages use one shared layout (`_layouts/default.html`, which carries the AdSense code, the top inquiry banner, nav and footer) plus includes in `_includes/`. Do **not** add a `.nojekyll` file.

Turn it on once: **Settings → Pages → Build and deployment → Source: Deploy from a branch → `main` / `(root)` → Save.** Live at `https://webworksa1.github.io/66223-com/`.

To regenerate every page after editing guide content or `_source/build.py`:

```
cd _source && python3 build_jekyll.py ..
```

(It only rewrites generated files; `_source/`, README and `.git` are left alone.)

## Custom domain (do this when ready)
1. DNS at your registrar: A records `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`; `www` CNAME → `webworksa1.github.io`.
2. In `_config.yml` set `url: "https://66223.com"` and `baseurl: ""`, and add a file named `CNAME` containing `66223.com`. (Rebuilding? Run `JEKYLL_URL=https://66223.com JEKYLL_BASEURL= python3 build_jekyll.py ..`.)
3. Settings → Pages → Custom domain `66223.com` → Enforce HTTPS.
4. Apply to AdSense with `66223.com` once the domain resolves.

## Donation buttons
Add PayPal / Stripe / Buy Me a Coffee links in the `PAY` object at the top of `assets/js/site.js` (and `_source/assets/js/site.js`) to show direct payment buttons on /donate/.

© 66223.com. "66223" is used descriptively as a USPS ZIP Code; no trademark is claimed in it. "ZIP Code" is a USPS trademark.
