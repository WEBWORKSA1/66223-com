# 66223.com

Independent living, relocation & home-money guide for ZIP 66223 (south Overland Park, Kansas). Static HTML/CSS/JS, hosted on GitHub Pages (free plan).

- **40 indexable pages**: home, 14 guides, 6 Kansas-specific calculators, multi-step lead funnel, data snapshot, videos, community, contests + official rules, donate, careers, advertise, list-your-business, about, contact, editorial policy, privacy, terms, disclaimer, sitemap.
- **Monetization**: Google AdSense (ca-pub-6620975821265271) in every page head + `ads.txt`; lead generation; sponsorships; donations.
- **Forms**: all forms post via FormSubmit AJAX to an address assembled at runtime — no email address appears in the HTML. The first submission triggers a one-time FormSubmit activation email; confirm it once.
- **Strategy + phase-wise build prompts**: see `BUILD-PROMPTS.md`.

## How it builds
Source lives in `_source/` (generator `build.py`, guide content, CSS/JS). Any push that changes `_source/` runs the **Build site** GitHub Action, which regenerates every page into the repo root and commits it. GitHub Pages serves the root of `main`.

Local build: `cd _source && SITE_URL=https://66223.com/ python3 build.py ..`

## Custom domain (do this when ready)
1. DNS at your registrar: A records `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`; `www` CNAME → `webworksa1.github.io`.
2. Repo Settings → Secrets and variables → Actions → Variables: add `SITE_URL` = `https://66223.com/` and `CNAME` = `66223.com`.
3. Actions → Build site → Run workflow. Then Settings → Pages → Enforce HTTPS.

## Donation buttons
Add PayPal / Stripe / Buy Me a Coffee links in the `PAY` object at the top of `_source/assets/js/site.js` to show direct payment buttons on /donate/.

© 66223.com. "66223" is used descriptively as a USPS ZIP Code; no trademark is claimed in it. "ZIP Code" is a USPS trademark.
