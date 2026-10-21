#!/usr/bin/env python3
"""66223.com static site generator.
Usage:  python3 build.py [OUT_DIR]
Env:    SITE_URL  (default https://66223.com/) — canonical base. Set to the github.io URL while DNS is not pointed.
"""
import os, re, sys, json, html, shutil, datetime

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(SRC, "..", "site-out"))
SITE_URL = os.environ.get("SITE_URL", "https://66223.com/").rstrip("/") + "/"
ADSENSE = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6620975821265271" crossorigin="anonymous"></script>'
TODAY = datetime.date.today().isoformat()
BRAND = "66223"
TAGLINE = "Overland Park living, moving & home-money guide"
INQUIRY_URL = "https://web.works/contact"

PAGES = []  # (path, title, priority)

# ----------------------------------------------------------------- icons
I = {
 "home": '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>',
 "calc": '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 7h8M8 11h2M12 11h2M16 11h0M8 15h2M12 15h2M16 15v3"/>',
 "map": '<path d="M9 4L3 6v14l6-2 6 2 6-2V4l-6 2-6-2z"/><path d="M9 4v14M15 6v14"/>',
 "tax": '<path d="M4 20V8l8-4 8 4v12"/><path d="M8 20v-6M12 20v-6M16 20v-6M3 20h18"/>',
 "truck": '<path d="M3 7h11v9H3zM14 10h4l3 3v3h-7"/><circle cx="7" cy="18" r="1.6"/><circle cx="17" cy="18" r="1.6"/>',
 "scale": '<path d="M12 3v18M5 7h14"/><path d="M5 7l-3 6a3 3 0 006 0zM19 7l-3 6a3 3 0 006 0z"/>',
 "key": '<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M17 6l3 3"/>',
 "tool": '<path d="M14.7 6.3a4 4 0 00-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 005.4-5.4l-2.5 2.5-2.4-.6-.6-2.4z"/>',
 "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
 "heart": '<path d="M12 20s-7-4.4-9-9a5 5 0 019-3 5 5 0 019 3c-2 4.6-9 9-9 9z"/>',
 "trophy": '<path d="M8 4h8v5a4 4 0 01-8 0z"/><path d="M8 6H4a3 3 0 003 4M16 6h4a3 3 0 01-3 4M12 13v4M8 21h8M9 17h6"/>',
 "users": '<circle cx="9" cy="8" r="3"/><path d="M3 20a6 6 0 0112 0"/><circle cx="17" cy="9" r="2.5"/><path d="M15.5 14a5 5 0 016 5"/>',
 "mega": '<path d="M3 10v4h3l6 4V6L6 10z"/><path d="M16 9a4 4 0 010 6M19 6a8 8 0 010 12"/>',
 "play": '<rect x="3" y="5" width="18" height="14" rx="3"/><path d="M10 9l5 3-5 3z"/>',
 "chart": '<path d="M4 20V4M4 20h16"/><path d="M8 16v-4M12 16V8M16 16v-6"/>',
 "book": '<path d="M4 5a2 2 0 012-2h13v16H6a2 2 0 00-2 2z"/><path d="M4 19V5"/>',
 "brief": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5h6v2M3 12h18"/>',
 "school": '<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v5c3 2 9 2 12 0v-5"/>',
 "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
 "search": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
 "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
 "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
 "camera": '<path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/>',
 "storm": '<path d="M7 15a5 5 0 110-10 6 6 0 0111 2 4 4 0 01-1 8z"/><path d="M12 13l-2 4h3l-2 4"/>',
}
def icon(name, cls="icon"):
    return f'<span class="{cls}" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{I[name]}</svg></span>'
def svg(name, size=20):
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{I[name]}</svg>'

e = html.escape

# ----------------------------------------------------------------- data
GUIDE_ORDER = [
 "moving-to-overland-park-66223","cost-of-living-66223","property-taxes-johnson-county-kansas","new-resident-checklist-66223",
 "buying-a-home-in-66223","selling-your-home-in-66223","rent-vs-buy-66223","mortgage-basics-kansas-homebuyers",
 "home-maintenance-calendar-kansas","hail-storm-roof-insurance-kansas","family-things-to-do-overland-park",
 "remote-work-life-66223","choosing-schools-66223","small-business-overland-park"]
CAT_ICON = {"Relocation":"map","Money & Taxes":"tax","Buying & Selling":"key","Home & Maintenance":"tool","Family & Lifestyle":"sun","Work & Business":"brief"}

TOOLS = [
 ("mortgage-calculator","Mortgage Payment Calculator","Full monthly payment with Kansas property tax, insurance, HOA and PMI built in.","calc","mortgage"),
 ("property-tax-estimator","Kansas Property Tax Estimator","Estimate a Johnson County tax bill using the 11.5% assessment rule and your mill levy.","tax","tax"),
 ("home-affordability-calculator","Home Affordability Calculator","How much house your income really supports — comfortable vs. stretch budget.","key","afford"),
 ("rent-vs-buy-calculator","Rent vs. Buy Calculator","Year-by-year wealth comparison with appreciation, selling costs and investing the difference.","scale","rentbuy"),
 ("moving-cost-estimator","Moving Cost Estimator","Ballpark ranges for full-service movers, containers and DIY trucks.","truck","moving"),
 ("cost-of-living-calculator","Cost of Living Salary Calculator","What salary you need in 66223 to keep your current lifestyle.","chart","col"),
]

VIDEOS = [
 ("_KSgP4_toaI","Pros and cons of living in Overland Park (2026)","Relocation","A current look at the trade-offs people weigh before moving here."),
 ("XszhaGzvE-o","Moving to Overland Park: complete map tour","Relocation","Orients you to the city's layout north to south — useful before you house-hunt."),
 ("UX6lUCzdFlM","A guide to Overland Park, Kansas","Relocation","Broad overview of why the city keeps landing on best-places lists."),
 ("GxSC5qW75zc","Should you move to Overland Park? Pros and cons","Relocation","A second opinion on the move — compare it with the one above."),
 ("_7ZJdCXPvaU","Living in Kansas City vs. Overland Park","Relocation","City-versus-suburb comparison for people torn between the two."),
 ("I9Nlqg3cTPo","Overland Park pros and cons — the tax question","Money","Discusses taxes as a downside; pair it with our property tax guide for the numbers."),
 ("fE2-slEjnz4","Overland Park Arboretum walking tour","Things to do","A virtual walk through the Arboretum & Botanical Gardens trails."),
 ("FQplp1c0BQY","Inside the LongHouse Visitor Center","Things to do","Tour of the Arboretum's visitor center."),
 ("E5j2AHCYP0s","Experience the Deanna Rose Children's Farmstead","Things to do","What a family visit to the farmstead looks like."),
 ("bOuDdxXvewE","The Overland Park Farmers' Market returns downtown","Things to do","Local news coverage of the market's return to Downtown OP."),
]

# ----------------------------------------------------------------- layout
def rel(depth): return "../" * depth if depth else "./"

def nav(root, current):
    items = [("guides/","Guides"),("tools/","Tools"),("data/","66223 Data"),("videos/","Videos"),("community/","Community"),("advertise/","Advertise")]
    lis = "".join(f'<li><a href="{root}{p}"{" aria-current=\"page\"" if current==p else ""}>{t}</a></li>' for p,t in items)
    return f'''<a class="skip" href="#main">Skip to content</a>
<div class="inquiry" role="note">Contact, if you are interested in this website / domain name / Sponsorship / Advertisement / Partnership — <a href="{INQUIRY_URL}" target="_blank" rel="noopener">contact here &rarr;</a></div>
<header class="site-header"><div class="wrap nav">
  <a class="brand" href="{root}" aria-label="66223 home"><span class="brand-mark">66223</span><span class="brand-text"><b>66223<span style="color:var(--wheat)">.com</span></b><small>Overland Park, KS</small></span></a>
  <button class="icon-btn menu-btn" aria-label="Open menu" aria-expanded="false">{svg("menu")}</button>
  <ul class="nav-links">{lis}<li class="nav-cta"><a class="btn btn-primary btn-sm" href="{root}get-matched/" style="color:#fff">Get matched free</a></li>
  <li><button class="icon-btn" data-theme-toggle aria-label="Toggle dark mode">{svg("sun",18)}</button></li></ul>
</div></header>'''

def footer(root):
    return f'''<footer class="site-footer"><div class="wrap">
<div class="footer-grid">
 <div><a class="brand" href="{root}" style="color:#fff"><span class="brand-mark">66223</span><span class="brand-text"><b>66223.com</b><small style="color:#9fb0a7">{TAGLINE}</small></span></a>
  <p style="margin-top:14px;max-width:34ch">Independent guides, calculators and local connections for people moving to, living in, and investing in ZIP 66223 — south Overland Park, Kansas.</p>
  <a class="btn btn-gold btn-sm" href="{root}get-matched/">Get matched with a local pro</a></div>
 <div><h4>Explore</h4><ul><li><a href="{root}guides/">All guides</a></li><li><a href="{root}tools/">Calculators</a></li><li><a href="{root}data/">66223 data snapshot</a></li><li><a href="{root}videos/">Videos</a></li><li><a href="{root}guides/moving-to-overland-park-66223/">Moving guide</a></li></ul></div>
 <div><h4>Community</h4><ul><li><a href="{root}contests/">Contests &amp; prizes</a></li><li><a href="{root}donate/">Support us</a></li><li><a href="{root}careers/">Join the team</a></li><li><a href="{root}community/">Community hub</a></li></ul></div>
 <div><h4>Business</h4><ul><li><a href="{root}advertise/">Advertise &amp; sponsor</a></li><li><a href="{root}list-your-business/">List your business</a></li><li><a href="{INQUIRY_URL}" target="_blank" rel="noopener">Buy / partner on this domain</a></li><li><a href="{root}contact/">Contact</a></li></ul></div>
 <div><h4>Company</h4><ul><li><a href="{root}about/">About</a></li><li><a href="{root}editorial-policy/">Editorial policy</a></li><li><a href="{root}privacy/">Privacy &amp; cookies</a></li><li><a href="{root}terms/">Terms of use</a></li><li><a href="{root}disclaimer/">Disclaimer &amp; trademarks</a></li><li><a href="{root}sitemap.html">Sitemap</a></li></ul></div>
</div>
<div class="legal-note">
 <p><strong>Independence &amp; trademark notice:</strong> 66223.com is an independent publication. It is not affiliated with, endorsed by, or operated by the City of Overland Park, Johnson County, the State of Kansas, the United States Postal Service, Blue Valley USD 229, or any business or creator mentioned on this site. “ZIP Code” is a registered trademark of the United States Postal Service; the number 66223 is used here only descriptively, to identify a geographic area. The site makes no claim of trademark or exclusive rights in the number “66223”. All third-party names, logos and videos belong to their respective owners and are referenced for identification and commentary. See our <a href="{root}disclaimer/">full disclosure</a>.</p>
 <p>Content is for general information only and is not legal, tax, financial, insurance or real-estate advice. Calculators give estimates. Verify important figures with official sources or a licensed professional. Some pages display advertising served by Google and may contain sponsored placements, which are always labeled.</p>
 <p>&copy; <span id="year">2026</span> 66223.com — original text, design and tools. All rights reserved. <a href="{INQUIRY_URL}" target="_blank" rel="noopener">Interested in this website or domain?</a> &middot; <button class="btn btn-ghost btn-sm theme-toggle" data-theme-toggle style="color:#e8efe9;border-color:#2a3832">Toggle dark mode</button></p>
</div></div></footer>
<div class="mobile-cta"><a class="btn btn-primary btn-block" href="{root}get-matched/" style="color:#fff">Get matched with a local pro — free</a></div>
<div class="cookie" role="dialog" aria-label="Cookie notice"><strong>Cookies &amp; ads.</strong> We use cookies for basic site features, and Google uses cookies to serve and measure ads. <a href="{root}privacy/">Learn more</a>.<div class="btns"><button class="btn btn-primary btn-sm" data-cookie="all" style="color:#fff">Accept</button><button class="btn btn-ghost btn-sm" data-cookie="essential">Essential only</button></div></div>'''

def page(path, title, desc, body, current="", depth=None, tool=None, schema=None, priority="0.6", og_type="website", noindex=False):
    if depth is None:
        depth = 0 if path in ("index.html","404.html","sitemap.html") else path.count("/")
    root = rel(depth)
    url = SITE_URL + ("" if path == "index.html" else path.replace("index.html",""))
    full_title = title if title.startswith("66223") else f"{title} | 66223.com"
    ld = [{"@context":"https://schema.org","@type":"WebSite","name":"66223.com","url":SITE_URL,"description":TAGLINE}] if path=="index.html" else []
    if schema: ld += schema if isinstance(schema, list) else [schema]
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in ld)
    body_attr = f' data-tool="{tool}"' if tool else ""
    tools_js = f'<script src="{root}assets/js/tools.js" defer></script>' if tool else ""
    robots = '<meta name="robots" content="noindex">' if noindex else '<meta name="robots" content="index,follow,max-image-preview:large">'
    doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
{robots}
<link rel="canonical" href="{url}">
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="66223.com"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{SITE_URL}assets/img/og.svg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#14532d">
<link rel="icon" href="{root}assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700;9..144,800&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/css/site.css">
{ADSENSE}
{ld_html}
</head>
<body{body_attr}>
{nav(root, current)}
<main id="main">
{body.replace("{{root}}", root)}
</main>
{footer(root)}
<script src="{root}assets/js/site.js" defer></script>
{tools_js}
</body>
</html>'''
    dest = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f: f.write(doc)
    if not noindex: PAGES.append((path, title, priority))

# ----------------------------------------------------------------- shared blocks
CONSENT = '<label class="check"><input type="checkbox" name="consent" value="yes" required> <span>I agree that 66223.com may share my request with up to three relevant local professionals (such as a real estate agent, lender, mover or contractor) who may contact me by phone, text or email about it. Consent is not a condition of any purchase. Message/data rates may apply. I can opt out anytime. See the <a href="{{root}}privacy/">Privacy Policy</a>.</span></label>'
HP = '<div class="hp" aria-hidden="true"><label>Leave empty<input type="text" name="_hp" tabindex="-1" autocomplete="off"></label></div>'

def quick_lead(title="Get matched with a vetted 66223 pro — free", sub="Tell us what you need. We connect you with up to three local specialists. No spam, no obligation.", source="quick"):
    return f'''<section class="lead-box reveal" aria-labelledby="lead-{source}">
 <div><span class="eyebrow" style="background:rgba(255,255,255,.12);color:#f2c66d">Free local matching</span>
  <h2 id="lead-{source}">{title}</h2><p>{sub}</p>
  <ul><li>Buyer &amp; seller agents who know south Overland Park</li><li>Lenders, insurance agents and movers</li><li>Roofers, HVAC, landscapers and other home pros</li></ul></div>
 <form class="form form-card" data-form="Quick lead ({source})" data-success="You're in. A local specialist will reach out within one business day.">
  {HP}<input type="hidden" name="source" value="{source}">
  <div class="field"><label for="ql-goal-{source}">I need help with</label>
   <select id="ql-goal-{source}" name="goal" required><option value="">Choose one…</option><option>Buying a home</option><option>Selling a home</option><option>Relocating to 66223</option><option>Mortgage or refinance</option><option>Home insurance</option><option>Moving company</option><option>Roofing / storm damage</option><option>Other home services</option></select></div>
  <div class="row2"><div class="field"><label for="ql-name-{source}">Name</label><input id="ql-name-{source}" type="text" name="name" autocomplete="name" required></div>
  <div class="field"><label for="ql-phone-{source}">Phone</label><input id="ql-phone-{source}" type="tel" name="phone" autocomplete="tel" required></div></div>
  <div class="field"><label for="ql-email-{source}">Email</label><input id="ql-email-{source}" type="email" name="email" autocomplete="email" required></div>
  {CONSENT}
  <button class="btn btn-primary btn-block" type="submit" style="color:#fff">Match me now</button>
  <p class="form-status" role="status" aria-live="polite"></p>
 </form></section>'''

INLINE_CTA = '''<aside class="inline-cta"><div><h3>Want a local pro to run your numbers?</h3><p>Free, no-obligation matching with agents, lenders, movers and home pros who work 66223.</p></div><a class="btn btn-primary" href="{{root}}get-matched/" style="color:#fff">Get matched free</a></aside>'''

def video_card(vid, title, cat, blurb):
    return f'''<figure class="reveal" style="margin:0"><div class="video" data-id="{vid}" data-title="{e(title)}" role="button" tabindex="0" aria-label="Play video: {e(title)}">
<img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="" loading="lazy" width="480" height="360"><span class="play"><i></i></span></div>
<figcaption class="video-caption"><strong>{e(title)}</strong><small>{e(blurb)} · Video by its creator on YouTube</small></figcaption></figure>'''

def page_hero(eyebrow, h1, lead, crumbs=None):
    bc = ""
    if crumbs:
        bc = '<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="{{root}}">Home</a> / ' + " / ".join(f'<a href="{{{{root}}}}{p}">{t}</a>' if p else e(t) for p,t in crumbs) + "</nav>"
    return f'<section class="page-hero"><div class="wrap">{bc}<span class="eyebrow">{eyebrow}</span><h1>{h1}</h1><p class="lead">{lead}</p></div></section>'

def crumbs_schema(items):
    return {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":SITE_URL+p} for i,(p,n) in enumerate(items)]}

# ----------------------------------------------------------------- guides
def load_guides():
    gd = os.path.join(SRC, "content", "guides")
    out = []
    for slug in GUIDE_ORDER:
        fp = os.path.join(gd, slug + ".html")
        if not os.path.exists(fp): print("MISSING GUIDE", slug); continue
        raw = open(fp, encoding="utf-8").read()
        meta = dict(re.findall(r"<!--(title|description|category|readtime|lede):\s*(.*?)-->", raw))
        body = re.sub(r"<!--(title|description|category|readtime|lede):.*?-->\s*", "", raw).strip()
        out.append({"slug":slug, "title":meta.get("title",slug), "desc":meta.get("description",""), "cat":meta.get("category","Relocation"),
                    "read":meta.get("readtime","6"), "lede":meta.get("lede",""), "body":body})
    return out

def guide_card(g, root="{{root}}"):
    return f'''<a class="card card-link reveal" data-guide data-cat="{e(g["cat"])}" href="{root}guides/{g["slug"]}/">{icon(CAT_ICON.get(g["cat"],"book"))}<span class="tag">{e(g["cat"])} · {g["read"]} min</span><h3>{e(g["title"])}</h3><p>{e(g["desc"])}</p><span class="more">Read guide &rarr;</span></a>'''

def build_guides(guides):
    for g in guides:
        body = g["body"]
        if "<!--CTA-->" in body: body = body.replace("<!--CTA-->", INLINE_CTA, 1)
        else: body += INLINE_CTA
        faqs = re.findall(r"<summary>(.*?)</summary>\s*<p>(.*?)</p>", body, re.S)
        related = [x for x in guides if x["slug"] != g["slug"] and x["cat"] == g["cat"]][:2]
        related += [x for x in guides if x["slug"] != g["slug"] and x not in related][: 3 - len(related)]
        art = f'''<div class="wrap"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="{{{{root}}}}">Home</a> / <a href="{{{{root}}}}guides/">Guides</a> / {e(g["cat"])}</nav></div>
<article class="wrap article-wrap" style="padding-bottom:20px">
 <div>
  <span class="eyebrow">{e(g["cat"])}</span>
  <h1>{e(g["title"])}</h1>
  <p class="lead" style="font-size:1.18rem;color:var(--ink-2)">{e(g["lede"])}</p>
  <div class="meta"><span>By the 66223.com editorial team</span><span>Updated {datetime.date.today().strftime("%B %Y")}</span><span>{g["read"]} min read</span><button class="pill" data-share>Share</button></div>
  <div class="prose">{body}</div>
  <p class="src" style="margin-top:28px">Figures cite public sources listed on our <a href="{{{{root}}}}data/">66223 data page</a>. This guide is general information, not professional advice. Found an error? <a href="{{{{root}}}}contact/">Tell us</a>.</p>
 </div>
 <aside class="sidebar">
  <div class="card toc"><h4 style="font-family:var(--font-body);font-size:.8rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)">On this page</h4><ol id="toc-list"></ol></div>
  <div class="card" style="background:var(--prairie);color:#fff;border:0"><h3 style="color:#fff">Free local match</h3><p style="color:#d8eadf">Agents, lenders, movers and home pros who know 66223.</p><a class="btn btn-gold btn-block" href="{{{{root}}}}get-matched/">Start in 60 seconds</a></div>
  <div class="card"><h4 style="font-family:var(--font-body);font-size:.8rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)">Run the numbers</h4><ul style="padding-left:1.1em;margin:0">{"".join(f'<li><a href="{{{{root}}}}tools/{t[0]}/">{t[1]}</a></li>' for t in TOOLS[:4])}</ul></div>
 </aside>
</article>
<section class="section-tight"><div class="wrap"><h2>Keep reading</h2><div class="grid g3">{"".join(guide_card(x) for x in related)}</div></div></section>
<section class="section-tight"><div class="wrap">{quick_lead(source="guide-"+g["slug"][:20])}</div></section>'''
        schema = [{"@context":"https://schema.org","@type":"Article","headline":g["title"],"description":g["desc"],"dateModified":TODAY,"author":{"@type":"Organization","name":"66223.com editorial team"},"publisher":{"@type":"Organization","name":"66223.com"},"mainEntityOfPage":SITE_URL+f"guides/{g['slug']}/"},
                  crumbs_schema([("", "Home"),("guides/","Guides"),(f"guides/{g['slug']}/", g["title"])])]
        if faqs:
            schema.append({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":re.sub("<.*?>","",q),"acceptedAnswer":{"@type":"Answer","text":re.sub("<.*?>","",a)}} for q,a in faqs]})
        page(f"guides/{g['slug']}/index.html", g["title"], g["desc"], art, current="guides/", schema=schema, priority="0.8", og_type="article")

    cats = sorted(set(g["cat"] for g in guides))
    pills = '<button class="pill on" data-cat="all">All</button>' + "".join(f'<button class="pill" data-cat="{e(c)}">{e(c)}</button>' for c in cats)
    body = page_hero("Guides", "Everything you need to know about life in 66223", "Original, practical guides on moving, money, homes and family life in south Overland Park — written to answer the questions people actually search for.", [("guides/","Guides")]) + f'''
<section class="section-tight"><div class="wrap">
 <div class="grid" style="grid-template-columns:minmax(0,1fr);gap:14px;margin-bottom:22px"><div class="search-box">{svg("search")}<input id="guide-search" type="text" placeholder="Search guides — taxes, schools, hail, moving…" aria-label="Search guides"></div><div class="pill-row" role="group" aria-label="Filter by category">{pills}</div></div>
 <div class="grid g3">{"".join(guide_card(g) for g in guides)}</div>
</div></section>
<section class="section"><div class="wrap">{quick_lead(source="guides-hub")}</div></section>'''
    page("guides/index.html", "Guides to living in 66223 & Overland Park", "Practical guides to moving to, living in and owning a home in ZIP 66223, south Overland Park, Kansas: taxes, costs, schools, buying, selling and more.", body, current="guides/", priority="0.9")

# ----------------------------------------------------------------- tools
def range_row(id_, label, val, mn, mx, step, fmt="usd", hint=""):
    h = f'<span class="hint">{hint}</span>' if hint else ""
    return f'<div class="field"><label for="{id_}">{label}</label><div class="range-row"><input type="range" id="{id_}" min="{mn}" max="{mx}" step="{step}" value="{val}" data-fmt="{fmt}"><output for="{id_}"></output></div>{h}</div>'
def num_field(id_, label, val, hint="", step="any"):
    h = f'<span class="hint">{hint}</span>' if hint else ""
    return f'<div class="field"><label for="{id_}">{label}</label><input type="number" inputmode="decimal" id="{id_}" value="{val}" step="{step}">{h}</div>'

MILLS_HINT = "Total mill levy on your tax statement (city + county + schools + state + other). Illustrative default — check your own bill."

TOOL_UI = {
 "mortgage": ( range_row("price","Home price",437500,100000,1500000,5000) + range_row("down","Down payment",20,0,50,1,"pct") + num_field("rate","Interest rate (%)",6.5,"Use a current quote from your lender.") +
   '<div class="field"><label for="term">Loan term</label><select id="term"><option value="30">30 years</option><option value="20">20 years</option><option value="15">15 years</option></select></div>' +
   num_field("mills","Total mill levy",120,MILLS_HINT) + num_field("insurance","Homeowners insurance ($/yr)",2400,"Kansas premiums reflect hail and wind risk — get real quotes.") + num_field("hoa","HOA dues ($/month)",50),
   '''<p class="kicker" style="color:#bcc8c1;margin:0">Estimated monthly payment</p><div class="big" id="out-total">$0</div><div class="bar" id="bar"></div>
   <div class="legend-row"><span><b style="background:#4ade80"></b>Principal &amp; interest</span><span><b style="background:#f2c66d"></b>Property tax</span><span><b style="background:#7aa2ff"></b>Insurance</span><span><b style="background:#f08a5d"></b>HOA + PMI</span></div>
   <dl style="margin-top:16px"><dt>Principal &amp; interest</dt><dd id="out-pi"></dd><dt>Property tax</dt><dd id="out-tax"></dd><dt>Insurance</dt><dd id="out-ins"></dd><dt>HOA</dt><dd id="out-hoa"></dd><dt>PMI (est. 0.6%/yr if &lt;20% down)</dt><dd id="out-pmi"></dd><dt>Down payment</dt><dd id="out-down"></dd><dt>Loan amount</dt><dd id="out-loan"></dd><dt>Total interest over loan</dt><dd id="out-interest"></dd></dl>'''),
 "tax": ( range_row("value","Appraised market value",437500,50000,2000000,5000) + num_field("mills","Total mill levy",120,MILLS_HINT) + num_field("citymills","City portion (mills)",14.5,"Overland Park's city levy is about 14.5 mills (2026)."),
   '''<p class="kicker" style="color:#bcc8c1;margin:0">Estimated annual property tax</p><div class="big" id="out-net">$0</div>
   <dl><dt>Per month (escrow)</dt><dd id="out-monthly"></dd><dt>Assessed value (11.5%)</dt><dd id="out-assessed"></dd><dt>Tax before exemption</dt><dd id="out-gross"></dd><dt>School-levy exemption ($75k × 20 mills)</dt><dd id="out-credit"></dd><dt>City of Overland Park share</dt><dd id="out-city"></dd><dt>Effective rate on value</dt><dd id="out-rate"></dd></dl>'''),
 "afford": ( num_field("income","Gross household income ($/yr)",113707,"66223 median household income is about $113,700 (ACS 2023).") + num_field("debts","Monthly debt payments ($)",600,"Car, student loans, minimum card payments.") +
   num_field("downamt","Cash for down payment ($)",60000) + num_field("rate","Interest rate (%)",6.5) + '<div class="field"><label for="term">Loan term</label><select id="term"><option value="30">30 years</option><option value="15">15 years</option></select></div>' +
   num_field("mills","Total mill levy",120,MILLS_HINT) + num_field("insurance","Homeowners insurance ($/yr)",2400),
   '''<p class="kicker" style="color:#bcc8c1;margin:0">Comfortable price (28/36 rule of thumb)</p><div class="big" id="out-price">$0</div>
   <dl><dt>Stretch price (33/43)</dt><dd id="out-stretch"></dd><dt>Max housing payment</dt><dd id="out-budget"></dd><dt>28% front-end limit</dt><dd id="out-front"></dd><dt>36% back-end room</dt><dd id="out-back"></dd><dt>Loan amount</dt><dd id="out-loan"></dd></dl>'''),
 "rentbuy": ( num_field("rent","Current rent ($/month)",1790,"BestPlaces typical 2-bedroom in 66223 ≈ $1,790.") + num_field("rentgrowth","Rent growth (%/yr)",3) + num_field("price","Home price ($)",437500) + num_field("down","Down payment (%)",20) +
   num_field("rate","Mortgage rate (%)",6.5) + num_field("mills","Total mill levy",120,MILLS_HINT) + num_field("insurance","Insurance ($/yr)",2400) + num_field("maint","Maintenance (% of value/yr)",1) +
   num_field("appr","Home appreciation (%/yr)",3) + num_field("invest","Renter's investment return (%/yr)",6) + range_row("years","Years you'll stay",7,1,30,1,"yr"),
   '''<p class="kicker" style="color:#bcc8c1;margin:0">After your stay</p><div class="big" id="out-verdict">—</div>
   <dl><dt>Gap in net wealth</dt><dd id="out-gap"></dd><dt>Buyer net equity (after 7% selling costs)</dt><dd id="out-buyer"></dd><dt>Renter invested portfolio</dt><dd id="out-renter"></dd><dt>Break-even year</dt><dd id="out-breakeven"></dd><dt>Mortgage P&amp;I</dt><dd id="out-pi"></dd><dt>Total rent paid</dt><dd id="out-rentpaid"></dd><dt>Total owner costs</dt><dd id="out-buypaid"></dd></dl>'''),
 "moving": ( range_row("miles","Distance (miles)",500,5,3000,5,"num") +
   '<div class="field"><label for="size">Home size</label><select id="size"><option value="studio">Studio</option><option value="1br">1 bedroom</option><option value="2br">2 bedrooms</option><option value="3br" selected>3 bedrooms</option><option value="4br">4+ bedrooms</option></select></div>' +
   '<div class="field"><label for="mode">How you\'ll move</label><select id="mode"><option value="full">Full-service movers</option><option value="container">Portable container</option><option value="diy">DIY rental truck</option></select></div>' +
   '<fieldset class="field" style="border:0;padding:0;margin:0"><legend class="legend">Extras</legend><label class="check"><input type="checkbox" name="extra" value="600"> Packing service</label><label class="check"><input type="checkbox" name="extra" value="300"> Piano or specialty item</label><label class="check"><input type="checkbox" name="extra" value="250"> Short-term storage (1 month)</label><label class="check"><input type="checkbox" name="extra" value="900"> Vehicle shipping</label></fieldset>',
   '''<p class="kicker" style="color:#bcc8c1;margin:0">Typical cost range</p><div class="big"><span id="out-low"></span>–<span id="out-high"></span></div>
   <dl><dt>Midpoint</dt><dd id="out-mid"></dd><dt>Estimated shipment weight</dt><dd id="out-weight"></dd></dl><p style="color:#bcc8c1;font-size:.85rem;margin-top:14px">Ballpark only, built from rule-of-thumb rates. Season, stairs and access change real quotes — always get 3 written estimates.</p>'''),
 "col": ( num_field("salary","Your current salary ($)",90000) + num_field("fromindex","Current city cost-of-living index",100,"100 = US average. Use any published index for your city.") + num_field("toindex","66223 cost-of-living index",106.2,"BestPlaces puts 66223 about 6.2% above the US average."),
   '''<p class="kicker" style="color:#bcc8c1;margin:0">Equivalent salary in 66223</p><div class="big" id="out-eq">$0</div><dl><dt>Difference</dt><dd id="out-diff"></dd><dt>Cost difference</dt><dd id="out-pct"></dd></dl>'''),
}
TOOL_NOTES = {
 "mortgage": "<h2>How this calculator works</h2><p>Principal and interest use the standard amortization formula. Property tax uses Kansas rules: residential property is assessed at 11.5% of appraised value, multiplied by your total mill levy and divided by 1,000, minus the exemption on the first $75,000 of value for the statewide 20-mill school levy. The default 120 mills is illustrative — your actual levy depends on the exact taxing districts on your tax statement.</p><p>PMI is shown at an illustrative 0.6% of the loan per year when the down payment is below 20%; real PMI depends on credit score and lender.</p><p>Read next: <a href=\"{{root}}guides/mortgage-basics-kansas-homebuyers/\">Mortgage basics for Kansas buyers</a> · <a href=\"{{root}}guides/buying-a-home-in-66223/\">Buying a home in 66223</a></p>",
 "tax": "<h2>The Kansas formula</h2><p><strong>Annual tax = appraised value × 11.5% × total mills ÷ 1,000 − school-levy exemption.</strong> The exemption removes the first $75,000 of a home's value from the statewide 20-mill school levy, worth about $172.50 per year. Overland Park's own city levy (about 14.5 mills for 2026) is the lowest of any Johnson County city and makes up only around 13% of a typical bill — the rest goes to the county, school district, state and other districts.</p><p>Your valuation comes from the Johnson County Appraiser's Office. If it looks too high, you can appeal after receiving your valuation notice. Full walk-through: <a href=\"{{root}}guides/property-taxes-johnson-county-kansas/\">Johnson County property taxes explained</a>.</p>",
 "afford": "<h2>Rules of thumb, not rules</h2><p>The comfortable figure keeps housing costs at or below 28% of gross monthly income and total debt payments at or below 36%. The stretch figure uses 33% / 43%, closer to what some lenders will approve. Approval is not the same as comfort — leave room for maintenance, childcare and savings.</p><p>Read next: <a href=\"{{root}}guides/rent-vs-buy-66223/\">Rent vs. buy in 66223</a> · <a href=\"{{root}}guides/cost-of-living-66223/\">Cost of living in 66223</a></p>",
 "rentbuy": "<h2>What the model assumes</h2><p>The buyer pays about 3% in closing costs, owns the home for the years you choose, then sells with roughly 7% in selling costs. The renter invests the would-be down payment and closing costs, plus any monthly savings versus owning, at the return you set. Change any input to stress-test the answer — appreciation and how long you stay usually matter most.</p><p>Read next: <a href=\"{{root}}guides/rent-vs-buy-66223/\">Rent vs. buy: a 66223 framework</a></p>",
 "moving": "<h2>Reading the estimate</h2><p>Local moves (under about 100 miles) are usually billed by the hour; long-distance moves by weight and distance. Containers and DIY trucks save money but cost you time and labor. The ranges here are rule-of-thumb estimates to help you budget — not quotes.</p><p>Read next: <a href=\"{{root}}guides/moving-to-overland-park-66223/\">Moving to Overland Park</a> · <a href=\"{{root}}guides/new-resident-checklist-66223/\">New-resident checklist</a></p>",
 "col": "<h2>Using a cost-of-living index</h2><p>Indexes set the US average at 100. Divide the destination index by your current one and multiply by your salary to find the income that buys the same lifestyle. Housing usually drives most of the difference, so check rents and home prices for the specific neighborhoods you're considering.</p><p>Read next: <a href=\"{{root}}guides/cost-of-living-66223/\">Cost of living in 66223</a> · <a href=\"{{root}}data/\">66223 data snapshot</a></p>",
}

def build_tools():
    for slug, name, desc, ic, key in TOOLS:
        inputs, result = TOOL_UI[key]
        body = page_hero("Free calculator", name, desc, [("tools/","Tools"),("",name)]) + f'''
<section class="section-tight"><div class="wrap tool">
 <form class="form form-card" onsubmit="return false" aria-label="{e(name)} inputs">{inputs}<p class="src">Estimates only — not a quote, loan approval, or tax bill.</p></form>
 <div class="result" aria-live="polite">{result}<a class="btn btn-gold btn-block" style="margin-top:20px" href="{{{{root}}}}get-matched/">Get exact numbers from a local pro</a></div>
</div></section>
<section class="section-tight"><div class="wrap prose">{TOOL_NOTES[key]}</div></section>
<section class="section-tight"><div class="wrap"><h2>More calculators</h2><div class="grid g3">{"".join(tool_card(t) for t in [x for x in TOOLS if x[0]!=slug][:3])}</div></div></section>
<section class="section"><div class="wrap">{quick_lead(source="tool-"+key)}</div></section>'''
        schema = [{"@context":"https://schema.org","@type":"WebApplication","name":name,"applicationCategory":"FinanceApplication","operatingSystem":"Any","offers":{"@type":"Offer","price":"0","priceCurrency":"USD"},"url":SITE_URL+f"tools/{slug}/"}]
        page(f"tools/{slug}/index.html", name, desc + " Free, instant, no sign-up.", body, current="tools/", tool=key, schema=schema, priority="0.8")
    body = page_hero("Calculators", "Free money tools for 66223 homeowners, buyers and renters", "Built around Kansas and Johnson County rules — property tax assessment, the school-levy exemption and real local medians as defaults.", [("tools/","Tools")]) + f'''
<section class="section-tight"><div class="wrap grid g3">{"".join(tool_card(t) for t in TOOLS)}</div></section>
<section class="section"><div class="wrap">{quick_lead(source="tools-hub")}</div></section>'''
    page("tools/index.html", "Free home & moving calculators for 66223", "Mortgage, Kansas property tax, affordability, rent vs. buy, moving cost and cost-of-living calculators with 66223 defaults.", body, current="tools/", priority="0.9")

def tool_card(t):
    slug, name, desc, ic, key = t
    return f'<a class="card card-link reveal" href="{{{{root}}}}tools/{slug}/">{icon(ic)}<h3>{e(name)}</h3><p>{e(desc)}</p><span class="more">Open calculator &rarr;</span></a>'

# ----------------------------------------------------------------- get matched (primary lead gen)
def build_get_matched():
    goals = [("buy","Buy a home","Agents + lenders"),("sell","Sell a home","Listing agents"),("relocate","Relocate here","Relocation pros"),
             ("mortgage","Mortgage / refi","Local lenders"),("insurance","Home insurance","Agents & brokers"),("moving","Hire movers","Local & long-distance"),
             ("roof","Roof / storm damage","Licensed roofers"),("services","Other home services","HVAC, lawn, repairs"),("rent","Find a rental","Leasing help")]
    choice = "".join(f'<label class="choice"><input type="radio" name="goal" value="{v}" required><span>{t}<small>{s}</small></span></label>' for v,t,s in goals)
    body = f'''<section class="hero" style="padding-top:40px"><div class="wrap hero-grid" style="align-items:start">
<div>
 <span class="eyebrow">Free · No obligation · 60 seconds</span>
 <h1>Get matched with the right 66223 pro.</h1>
 <p class="lead">One short form connects you with up to three local specialists who actually work south Overland Park — so you stop cold-calling and start comparing.</p>
 <div class="grid g2" style="margin:26px 0">
  <div class="card">{icon("key")}<h3>Buyers &amp; sellers</h3><p>Agents who know Blue Valley-area neighborhoods, HOAs and pricing.</p></div>
  <div class="card">{icon("calc")}<h3>Money</h3><p>Lenders and insurance agents who quote Kansas hail and tax realities upfront.</p></div>
  <div class="card">{icon("truck")}<h3>Moving</h3><p>Local and long-distance movers, containers and storage.</p></div>
  <div class="card">{icon("tool")}<h3>Home services</h3><p>Roofing, HVAC, lawn, repairs — pros who serve 66223.</p></div>
 </div>
 <div class="notice"><strong>How it works:</strong> 1) Tell us what you need. 2) We review it and pass it to up to three relevant local pros. 3) They contact you; you choose. We never sell your details to a list broker.</div>
</div>
<form class="form form-card multistep" data-form="Get matched (full lead)" data-success="Request received. Expect a call or text from a matched local specialist within one business day." aria-label="Get matched form">
 {HP}<input type="hidden" name="source" value="get-matched">
 <div class="steps-bar" aria-hidden="true"><i></i><i></i><i></i></div>
 <div class="step"><p class="legend" style="font-size:1.1rem">Step 1 of 3 — What can we help with?</p><div class="choices c3">{choice}</div>
  <div class="step-nav"><span></span><button class="btn btn-primary" data-next style="color:#fff">Continue &rarr;</button></div></div>
 <div class="step"><p class="legend" style="font-size:1.1rem">Step 2 of 3 — A few details</p>
  <div class="field"><label for="gm-timeline">Timeline</label><select id="gm-timeline" name="timeline" required><option value="">Select…</option><option>ASAP / within 30 days</option><option>1–3 months</option><option>3–6 months</option><option>6+ months / just researching</option></select></div>
  <div data-goal="buy relocate rent" class="hidden"><div class="field"><label for="gm-budget">Budget</label><select id="gm-budget" name="budget" disabled><option>Under $300k</option><option>$300k–$450k</option><option selected>$450k–$650k</option><option>$650k–$900k</option><option>$900k+</option><option>Rent under $1,800/mo</option><option>Rent $1,800–$2,500/mo</option><option>Rent $2,500+/mo</option></select></div>
   <div class="field"><label for="gm-pre">Pre-approved for a mortgage?</label><select id="gm-pre" name="preapproved" disabled><option>Not yet</option><option>Yes</option><option>Paying cash</option><option>Not applicable</option></select></div></div>
  <div data-goal="sell" class="hidden"><div class="field"><label for="gm-val">Estimated home value</label><select id="gm-val" name="home_value" disabled><option>Under $350k</option><option selected>$350k–$500k</option><option>$500k–$750k</option><option>$750k+</option><option>Not sure — want a valuation</option></select></div></div>
  <div data-goal="mortgage insurance" class="hidden"><div class="field"><label for="gm-loan">Purpose</label><select id="gm-loan" name="finance_purpose" disabled><option>New purchase</option><option>Refinance</option><option>Cash-out / HELOC</option><option>Insurance quote / re-shop</option></select></div></div>
  <div data-goal="moving" class="hidden"><div class="field"><label for="gm-from">Moving from (city / state)</label><input id="gm-from" type="text" name="moving_from" disabled></div><div class="field"><label for="gm-size">Home size</label><select id="gm-size" name="home_size" disabled><option>Studio/1BR</option><option>2BR</option><option selected>3BR</option><option>4BR+</option></select></div></div>
  <div data-goal="roof services" class="hidden"><div class="field"><label for="gm-svc">Service needed</label><select id="gm-svc" name="service" disabled><option>Roof inspection / hail damage</option><option>Roof replacement</option><option>HVAC</option><option>Plumbing</option><option>Electrical</option><option>Lawn / landscaping</option><option>Gutters</option><option>Painting</option><option>Handyman</option><option>Other</option></select></div></div>
  <div class="field"><label for="gm-notes">Anything else? <span class="hint">(optional)</span></label><textarea id="gm-notes" name="notes" placeholder="Neighborhood, must-haves, questions…"></textarea></div>
  <div class="step-nav"><button class="btn btn-ghost" data-prev>&larr; Back</button><button class="btn btn-primary" data-next style="color:#fff">Continue &rarr;</button></div></div>
 <div class="step"><p class="legend" style="font-size:1.1rem">Step 3 of 3 — Where should pros reach you?</p>
  <div class="row2"><div class="field"><label for="gm-first">First name</label><input id="gm-first" type="text" name="first_name" autocomplete="given-name" required></div><div class="field"><label for="gm-last">Last name</label><input id="gm-last" type="text" name="last_name" autocomplete="family-name" required></div></div>
  <div class="field"><label for="gm-email">Email</label><input id="gm-email" type="email" name="email" autocomplete="email" required></div>
  <div class="row2"><div class="field"><label for="gm-phone">Mobile phone</label><input id="gm-phone" type="tel" name="phone" autocomplete="tel" required></div><div class="field"><label for="gm-zip">Your current ZIP</label><input id="gm-zip" type="text" name="current_zip" inputmode="numeric" maxlength="10" autocomplete="postal-code" required></div></div>
  <div class="field"><label for="gm-contact">Best way to reach you</label><select id="gm-contact" name="contact_pref"><option>Call</option><option>Text</option><option>Email</option></select></div>
  {CONSENT}
  <div class="step-nav"><button class="btn btn-ghost" data-prev>&larr; Back</button><button class="btn btn-gold" type="submit">Get my matches</button></div>
  <p class="form-status" role="status" aria-live="polite"></p></div>
</form></div></section>
<section class="section-tight"><div class="wrap grid g3">
 <div class="card"><h3>Why 66223 pros?</h3><p>The ZIP's median home value is about $402,500 (ACS 2023) and climbing. Hyper-local experience on pricing, HOAs and school boundaries matters.</p></div>
 <div class="card"><h3>Your data, handled carefully</h3><p>We share your request only with the few pros relevant to it. No lists, no resale. Opt out anytime — see our <a href="{{{{root}}}}privacy/">privacy policy</a>.</p></div>
 <div class="card"><h3>Are you a local pro?</h3><p>Want requests like these? <a href="{{{{root}}}}list-your-business/">Apply to join the 66223 pro network</a>.</p></div>
</div></section>'''
    page("get-matched/index.html", "Get matched with a local 66223 pro — free", "Free matching with up to three local real estate agents, lenders, insurance agents, movers or home-service pros serving 66223, Overland Park.", body, current="get-matched/", priority="0.9")

# ----------------------------------------------------------------- data
def build_data():
    rows = [("Population (2020 Census)","24,843","zip-codes.com / U.S. Census 2020 DHC"),("Households","9,836 (avg. 2.53 people)","zip-codes.com / Census 2020"),
            ("Median household income","$113,707","ACS 2023 via us-databases.com"),("Median home value","$402,500 (ACS 2023) · $437,500 (2024)","us-databases.com; zip-codes.com"),
            ("Home value in 2011","$263,300","zip-codes.com"),("Median gross rent","$1,718","zip-codes.com"),("Typical 2-bedroom rent","≈ $1,790/mo","BestPlaces"),
            ("Owner vs. renter occupied","~56% / ~44%","zip-codes.com"),("Bachelor's degree or higher (25+)","~67%","zip-codes.com"),("Unemployment rate","~3.3%","ACS 2023 via us-databases.com"),
            ("Businesses / employees in ZIP","~825 / ~11,944","zip-codes.com"),("Cost of living vs. US","~6.2% higher","BestPlaces"),("Walk Score","33 (car-dependent)","Redfin"),
            ("Public school district","Blue Valley USD 229","Statistical Atlas"),("Time zone / area code","Central / 913","zip-codes.com"),
            ("Neighboring ZIPs","66085, 66209, 66213, 66221, 66224","Statistical Atlas")]
    city = [("Niche — Best Cities to Live in America 2026","#10"),("WalletHub — Best Places to Raise a Family 2026","#2"),("Livability — Best Places to Live in the U.S. 2025","#6"),
            ("City property tax (mill levy), 2026","~14.5 mills — lowest of any Johnson County city"),("Average homeowner's city tax, 2026","≈ $880"),("Combined sales tax rate","9.35%"),
            ("Johnson County levy (FY2025)","~24.1 mills — lowest county rate in Kansas"),("City parks","80+")]
    stat = lambda v,l,s: f'<div class="card stat reveal"><b>{v}</b><span>{l}</span><small>{s}</small></div>'
    body = page_hero("Data snapshot", "66223 by the numbers", "The key facts about ZIP 66223 — people, money, housing and the city around it — with every figure sourced. Use it to sanity-check any move or purchase.", [("data/","66223 Data")]) + f'''
<section class="section-tight"><div class="wrap grid g4">{stat("$113.7k","Median household income","ACS 2023")}{stat("$437.5k","Median home value (2024)","zip-codes.com")}{stat("67%","Adults with a bachelor's+","zip-codes.com")}{stat("#2","Best US city to raise a family","WalletHub 2026 (Overland Park)")}</div></section>
<section class="section-tight"><div class="wrap"><h2>ZIP 66223 profile</h2><div class="table-scroll"><table class="data"><thead><tr><th>Measure</th><th>Value</th><th>Source</th></tr></thead><tbody>{"".join(f"<tr><td>{a}</td><td><strong>{b}</strong></td><td class='src'>{c}</td></tr>" for a,b,c in rows)}</tbody></table></div>
<p class="src">Different datasets use different survey years and methods, so figures can disagree slightly. Census and ACS numbers are estimates with margins of error.</p></div></section>
<section class="section-tight"><div class="wrap"><h2>Overland Park &amp; Johnson County context</h2><div class="table-scroll"><table class="data"><thead><tr><th>Measure</th><th>Value</th></tr></thead><tbody>{"".join(f"<tr><td>{a}</td><td><strong>{b}</strong></td></tr>" for a,b in city)}</tbody></table></div>
<p class="src">Sources: Niche (2026), WalletHub via FOX4 Kansas City (2026), Livability via City of Overland Park (2025), Johnson County Post (city budget, 2026), City of Overland Park (sales tax), Johnson County Government (FY2025 budget).</p></div></section>
<section class="section-tight"><div class="wrap prose"><h2>What the numbers mean</h2>
<p><strong>It's an affluent, educated, owner-leaning ZIP — but not all owners.</strong> Two-thirds of adults hold at least a bachelor's degree and household income runs roughly 50% above the national median, yet about 44% of homes are rented. That mix supports both a strong resale market and steady rental demand.</p>
<p><strong>Home values have climbed fast.</strong> The median value rose from about $263,300 in 2011 to about $437,500 in 2024. For buyers, that means affordability depends heavily on rates and taxes — run your own scenario in the <a href="{{{{root}}}}tools/mortgage-calculator/">mortgage calculator</a>. For owners, it means it's worth checking your valuation each year; see <a href="{{{{root}}}}guides/property-taxes-johnson-county-kansas/">how Johnson County property taxes work</a>.</p>
<p><strong>Plan on driving.</strong> A Walk Score of 33 means most errands need a car. Factor two vehicles into your budget if you have a two-commuter household.</p>
<p><strong>Taxes: low city levy, full bill still meaningful.</strong> Overland Park's city levy is the lowest in Johnson County, but the city is only around 13% of a property tax bill. Schools, the county and the state make up the rest, which is why the total bill is what you should budget for.</p></div></section>
<section class="section"><div class="wrap">{quick_lead(source="data")}</div></section>'''
    page("data/index.html", "66223 ZIP code data: income, home values, rent, schools", "Sourced snapshot of ZIP 66223 in Overland Park, KS: population, median income, home values, rent, education, taxes and city rankings.", body, current="data/", priority="0.9",
         schema=[{"@context":"https://schema.org","@type":"Dataset","name":"ZIP 66223 snapshot","description":"Key public statistics for ZIP 66223, Overland Park, Kansas.","creator":{"@type":"Organization","name":"66223.com"}}])

# ----------------------------------------------------------------- videos
def build_videos():
    cats = []
    for v in VIDEOS:
        if v[2] not in cats: cats.append(v[2])
    sections = "".join(f'<section class="section-tight"><div class="wrap"><h2>{c}</h2><div class="grid g3">{"".join(video_card(*v[:2], v[2], v[3]) for v in VIDEOS if v[2]==c)}</div></div></section>' for c in cats)
    body = page_hero("Watch", "Videos about living in Overland Park &amp; 66223", "A curated watch list for people sizing up a move or looking for things to do. Videos are embedded from YouTube and belong to their creators; our notes tell you why each one is worth your time.", [("videos/","Videos")]) + sections + f'''
<section class="section-tight"><div class="wrap notice">Are you a local creator? Want your video featured or reviewed? <a href="{{{{root}}}}contact/">Submit it here</a>. Creators can also request removal of an embed at any time.</div></section>
<section class="section"><div class="wrap">{quick_lead(source="videos")}</div></section>'''
    page("videos/index.html", "Overland Park & 66223 videos: tours, pros and cons, things to do", "Curated videos on moving to Overland Park, Kansas: map tours, pros and cons, the Arboretum, Deanna Rose Farmstead and the farmers' market.", body, current="videos/", priority="0.7")

# ----------------------------------------------------------------- community, contests, donate, careers
CONTEST_END = "2027-01-31T23:59:00-06:00"
def build_community():
    body = page_hero("Community", "Built with 66223, for 66223", "Enter contests, nominate great local pros, support the project or join the team. Every program here is open, free to join and clearly explained.", [("community/","Community")]) + f'''
<section class="section-tight"><div class="wrap grid g2">
 <a class="card card-link reveal" href="{{{{root}}}}contests/">{icon("trophy")}<span class="tag">Open now</span><h3>Contests &amp; prizes</h3><p>Season 1: “66223 in Focus” photo contest plus Best Local Pro nominations. Free to enter.</p><span class="more">See contests &rarr;</span></a>
 <a class="card card-link reveal" href="{{{{root}}}}donate/">{icon("heart")}<span class="tag">Support</span><h3>Support the project</h3><p>Help keep guides free and ad-light, fund prizes and grow local coverage.</p><span class="more">Ways to give &rarr;</span></a>
 <a class="card card-link reveal" href="{{{{root}}}}careers/">{icon("users")}<span class="tag">Hiring</span><h3>Join the team</h3><p>Paid and volunteer roles for writers, photographers, video creators and sponsorship sellers.</p><span class="more">Open roles &rarr;</span></a>
 <a class="card card-link reveal" href="{{{{root}}}}advertise/">{icon("mega")}<span class="tag">Business</span><h3>Advertise &amp; sponsor</h3><p>Reach people actively moving to and buying in 66223 with clearly labeled sponsorships.</p><span class="more">Packages &rarr;</span></a>
</div></section>
<section class="section-tight"><div class="wrap"><div class="form-card">
 <h2>Get the 66223 monthly brief</h2><p>New guides, contest announcements, and the month's most useful local money tip. One email a month. Unsubscribe anytime.</p>
 <form class="form" data-form="Newsletter signup" data-success="You're subscribed. Watch for the next 66223 brief." style="grid-template-columns:1fr auto;align-items:end">{HP}
  <div class="field"><label for="nl-email">Email</label><input id="nl-email" type="email" name="email" required autocomplete="email"></div><button class="btn btn-primary" type="submit" style="color:#fff">Subscribe</button><p class="form-status" role="status" aria-live="polite" style="grid-column:1/-1"></p></form>
</div></div></section>'''
    page("community/index.html", "66223 community hub: contests, support, careers", "Join the 66223.com community: contests with prizes, local pro nominations, ways to support the project, and open roles.", body, current="community/", priority="0.7")

    body = page_hero("Contests", "Season 1: “66223 in Focus”", "Show us the best of south Overland Park through your lens — parks, seasons, neighborhoods, community moments. Free to enter. Sponsor-funded prizes.", [("community/","Community"),("contests/","Contests")]) + f'''
<section class="section-tight"><div class="wrap grid g2" style="align-items:start">
<div>
 <h2>Entries close in</h2>
 <div class="countdown" data-countdown="{CONTEST_END}"><div><b>00</b><span>Days</span></div><div><b>00</b><span>Hours</span></div><div><b>00</b><span>Min</span></div><div><b>00</b><span>Sec</span></div></div>
 <p class="kicker" style="margin-top:10px">Deadline: January 31, 2027, 11:59 p.m. Central.</p>
 <div class="grid g3" style="margin:22px 0">
  <div class="card stat"><b>$250</b><span>1st place gift card</span></div><div class="card stat"><b>$100</b><span>2nd place gift card</span></div><div class="card stat"><b>$50</b><span>3rd place gift card</span></div></div>
 <h3>Categories</h3><ul><li><strong>Seasons of 66223</strong> — landscapes, parks, weather</li><li><strong>Neighbors &amp; community</strong> — events, markets, volunteers (with consent of people pictured)</li><li><strong>Home &amp; garden</strong> — yards, curb appeal, gardens</li></ul>
 <h3>How judging works</h3><p>A panel scores entries on originality (40%), sense of place (30%) and technical quality (30%). Top entries are featured on 66223.com with photographer credit. People's Choice gets a featured spotlight.</p>
 <h3>Also open: Best Local Pro nominations</h3><p>Nominate a contractor, agent, lender, mover or small business that did great work in 66223. Winners get a free featured listing for three months.</p>
 <p class="kicker">No purchase necessary. 18+ and legal U.S. residents. Read the <a href="{{{{root}}}}contests/official-rules/">official rules</a>. Want to fund a prize or title-sponsor a season? <a href="{{{{root}}}}advertise/">Sponsor the contest</a>.</p>
</div>
<div class="grid" style="gap:20px">
 <form class="form form-card" data-form="Contest entry — 66223 in Focus" data-success="Entry received. We'll confirm by email and may ask for the full-resolution file.">{HP}
  <h3>Enter the photo contest</h3>
  <div class="row2"><div class="field"><label for="c-name">Full name</label><input id="c-name" type="text" name="name" required autocomplete="name"></div><div class="field"><label for="c-email">Email</label><input id="c-email" type="email" name="email" required autocomplete="email"></div></div>
  <div class="field"><label for="c-cat">Category</label><select id="c-cat" name="category" required><option value="">Choose…</option><option>Seasons of 66223</option><option>Neighbors &amp; community</option><option>Home &amp; garden</option></select></div>
  <div class="field"><label for="c-link">Link to your photo</label><input id="c-link" type="url" name="photo_link" required placeholder="https:// (Google Drive, Dropbox, Flickr, Instagram…)"><span class="hint">Make sure the link is viewable. Max 3 entries per person.</span></div>
  <div class="field"><label for="c-title">Title &amp; where it was taken</label><input id="c-title" type="text" name="title" required></div>
  <label class="check"><input type="checkbox" name="rules" value="accepted" required> <span>I'm 18+, I took this photo, I have consent from any identifiable people, and I accept the official rules.</span></label>
  <button class="btn btn-gold" type="submit">Submit my entry</button><p class="form-status" role="status" aria-live="polite"></p></form>
 <form class="form form-card" data-form="Best Local Pro nomination" data-success="Thanks — nomination received.">{HP}
  <h3>Nominate a Best Local Pro</h3>
  <div class="row2"><div class="field"><label for="n-biz">Business / pro name</label><input id="n-biz" type="text" name="business" required></div><div class="field"><label for="n-type">Type</label><select id="n-type" name="type"><option>Real estate agent</option><option>Lender</option><option>Contractor / home pro</option><option>Mover</option><option>Small business</option></select></div></div>
  <div class="field"><label for="n-why">Why they deserve it</label><textarea id="n-why" name="reason" required></textarea></div>
  <div class="row2"><div class="field"><label for="n-name">Your name</label><input id="n-name" type="text" name="name" required></div><div class="field"><label for="n-email">Your email</label><input id="n-email" type="email" name="email" required></div></div>
  <button class="btn btn-primary" type="submit" style="color:#fff">Send nomination</button><p class="form-status" role="status" aria-live="polite"></p></form>
</div></div></section>'''
    page("contests/index.html", "66223 in Focus photo contest — win prizes", "Free photo contest for south Overland Park: $250, $100 and $50 gift-card prizes, plus Best Local Pro nominations. 18+ U.S. residents.", body, current="community/", priority="0.7")

    rules = page_hero("Official rules", "“66223 in Focus” Season 1 — official rules", "Please read these rules before entering. By entering you agree to them.", [("contests/","Contests"),("","Official rules")]) + f'''
<section class="section-tight"><div class="wrap prose">
<p><strong>NO PURCHASE OR PAYMENT OF ANY KIND IS NECESSARY TO ENTER OR WIN. A PURCHASE OR DONATION WILL NOT INCREASE YOUR CHANCES OF WINNING. VOID WHERE PROHIBITED.</strong></p>
<h2>1. Sponsor</h2><p>The contest is sponsored by the publisher of 66223.com (“Sponsor”). Contact the Sponsor through the <a href="{{{{root}}}}contact/">contact page</a>. The contest is not sponsored, endorsed or administered by any city, school district, social network or photo-hosting service.</p>
<h2>2. Eligibility</h2><p>Open to legal residents of the 50 United States and D.C. who are 18 or older at the time of entry. Employees and contractors of Sponsor and their immediate household members are not eligible.</p>
<h2>3. Entry period</h2><p>Entries are accepted from November 1, 2026 through January 31, 2027, 11:59 p.m. Central Time. Sponsor's clock is the official timekeeper.</p>
<h2>4. How to enter</h2><p>Submit the entry form on the contest page with a viewable link to an original photograph. Limit three (3) entries per person. Photos must be taken in or near ZIP 66223 / Overland Park, Kansas.</p>
<h2>5. Entry requirements</h2><ul><li>You must be the sole author and copyright owner of the photo.</li><li>You must have permission from any identifiable person pictured (and from a parent or guardian for any minor).</li><li>No nudity, hateful content, trademarks used as the main subject, or content that violates any law or third-party right.</li><li>Light editing is fine; composites must be disclosed.</li></ul>
<h2>6. Judging</h2><p>A panel selected by Sponsor will score eligible entries: originality (40%), sense of place (30%), technical quality (30%). Ties are broken by the originality score. Judges' decisions are final.</p>
<h2>7. Prizes</h2><p>First place: one $250 gift card. Second place: one $100 gift card. Third place: one $50 gift card. Gift card brand chosen by Sponsor. Approximate retail value of all prizes: $400. Prizes may be funded by named contest sponsors. No cash substitution or transfer except at Sponsor's discretion; Sponsor may substitute a prize of equal or greater value. Winners are responsible for any taxes.</p>
<h2>8. Winner notification</h2><p>Winners will be notified by email within 30 days after the entry period ends and must respond within 14 days, or an alternate winner may be selected.</p>
<h2>9. License to use your photo</h2><p>You keep your copyright. By entering, you grant Sponsor a non-exclusive, royalty-free license to display your photo, with credit, on 66223.com and its social channels in connection with the contest and the site, for up to three years.</p>
<h2>10. Privacy</h2><p>Entry information is used to run the contest and contact winners, as described in our <a href="{{{{root}}}}privacy/">Privacy Policy</a>.</p>
<h2>11. General conditions</h2><p>Sponsor may cancel, modify or suspend the contest if fraud, technical failure or other factors impair its integrity, and may disqualify entries that break these rules. By entering, entrants release Sponsor from liability for any injury or loss arising from participation or prize use, to the extent permitted by law.</p>
<h2>12. Winners list</h2><p>Winners will be posted on the contest page after verification.</p>
</div></section>'''
    page("contests/official-rules/index.html", "Official contest rules — 66223 in Focus", "Official rules for the 66223 in Focus photo contest: eligibility, entry period, judging, prizes and conditions.", rules, current="community/", priority="0.4")

    amounts = "".join(f'<label class="choice"><input type="radio" name="tier" value="{v}" data-amount{" checked" if v=="25" else ""}><span>{l}</span></label>' for v,l in [("5","$5"),("25","$25"),("50","$50"),("100","$100"),("250","$250"),("custom","Other")])
    body = page_hero("Support", "Keep 66223.com free, useful and independent", "Your support pays for research, original photography, contest prizes and new tools — and keeps our guides free for every neighbor and newcomer.", [("community/","Community"),("donate/","Support")]) + f'''
<section class="section-tight"><div class="wrap grid g2" style="align-items:start">
<div>
 <h2>Where support goes</h2>
 <div class="table-scroll"><table class="data"><thead><tr><th>Use</th><th>Share</th><th>What it funds</th></tr></thead><tbody>
  <tr><td>Ongoing operations</td><td>35%</td><td>Hosting, data subscriptions, fact-checking, tools maintenance</td></tr>
  <tr><td>Contests &amp; prizes</td><td>20%</td><td>Seasonal prizes and community recognition</td></tr>
  <tr><td>Hiring local talent</td><td>25%</td><td>Paying local writers, photographers and video creators</td></tr>
  <tr><td>Promotion &amp; marketing</td><td>20%</td><td>Getting free guides in front of new residents</td></tr></tbody></table></div>
 <h3>Support tiers</h3>
 <div class="grid g3">
  <div class="card tier"><span class="tag">Supporter</span><div class="price">$5<small>/mo</small></div><p>Thanks in our supporter list.</p></div>
  <div class="card tier featured"><span class="badge">Most popular</span><span class="tag">Neighbor</span><div class="price">$25<small>/mo</small></div><p>Supporter list + early contest announcements.</p></div>
  <div class="card tier"><span class="tag">Champion</span><div class="price">$100<small>/mo</small></div><p>All of the above + name a monthly contest prize.</p></div></div>
 <p class="kicker" style="margin-top:14px">66223.com is an independent publication, not a registered charity. Contributions are not tax-deductible.</p>
</div>
<div class="form-card">
 <h3>Make a contribution</h3>
 <div id="pay-direct" class="hidden" style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:16px"></div>
 <form class="form" data-form="Support pledge" data-success="Thank you! We'll send you a secure payment link within one business day.">{HP}
  <fieldset class="field" style="border:0;padding:0;margin:0"><legend class="legend">Amount</legend><div class="amounts">{amounts}</div></fieldset>
  <input type="hidden" id="donate-amount" name="amount" value="25">
  <div class="field hidden" id="custom-amount-wrap"><label for="d-custom">Custom amount ($)</label><input id="d-custom" type="number" name="custom_amount" min="1"></div>
  <div class="field"><label for="d-freq">Frequency</label><select id="d-freq" name="frequency"><option>One-time</option><option>Monthly</option><option>Annual</option></select></div>
  <div class="field"><label for="d-purpose">Direct my support to</label><select id="d-purpose" name="purpose"><option>Wherever it's needed most</option><option>Operations</option><option>Contests &amp; prizes</option><option>Hiring local talent</option><option>Promotion &amp; marketing</option></select></div>
  <div class="row2"><div class="field"><label for="d-name">Name</label><input id="d-name" type="text" name="name" required></div><div class="field"><label for="d-email">Email</label><input id="d-email" type="email" name="email" required></div></div>
  <label class="check"><input type="checkbox" name="public_thanks" value="yes"> List my name on the supporter page</label>
  <button class="btn btn-gold btn-block" type="submit">Continue to secure payment</button>
  <p class="form-status" role="status" aria-live="polite"></p>
  <p class="src">We never ask for card details on this site. You'll receive a link to a secure payment processor.</p></form>
</div></div></section>
<section class="section-tight"><div class="wrap notice">Businesses: looking for visibility in return? See <a href="{{{{root}}}}advertise/">sponsorship packages</a> instead.</div></section>'''
    page("donate/index.html", "Support 66223.com", "Support independent local guides for 66223 and Overland Park. Fund operations, contest prizes, local talent and outreach.", body, current="community/", priority="0.5")

    roles = [("Local contributing writer","Freelance · per article","Write practical, sourced guides on housing, money, schools and local life. Kansas City metro experience preferred."),
             ("Photographer","Freelance · per shoot","Original photography of 66223 parks, seasons and neighborhoods for guides and social."),
             ("Video creator","Freelance · per video","Short neighborhood tours and explainers for YouTube and social channels."),
             ("Sponsorship &amp; partnerships rep","Commission","Sell clearly labeled sponsorships to agents, lenders and home-service businesses in Johnson County."),
             ("Community &amp; contest coordinator","Part-time / volunteer","Run seasonal contests, nominations and newsletter."),
             ("Web developer","Freelance / volunteer","Improve calculators, accessibility and performance on a static HTML stack.")]
    cards = "".join(f'<div class="card reveal"><span class="tag">{t}</span><h3>{r}</h3><p>{d}</p></div>' for r,t,d in roles)
    body = page_hero("Careers", "Join the 66223 team", "We're building the most useful independent guide to south Overland Park. If you know the area and do great work, we'd like to hear from you.", [("community/","Community"),("careers/","Careers")]) + f'''
<section class="section-tight"><div class="wrap grid g3">{cards}</div></section>
<section class="section-tight"><div class="wrap"><form class="form form-card" data-form="Job application" data-success="Application received. We review every application and reply within two weeks." style="max-width:760px">{HP}
 <h2>Apply</h2>
 <div class="row2"><div class="field"><label for="j-name">Full name</label><input id="j-name" type="text" name="name" required></div><div class="field"><label for="j-email">Email</label><input id="j-email" type="email" name="email" required></div></div>
 <div class="row2"><div class="field"><label for="j-role">Role</label><select id="j-role" name="role" required><option value="">Choose…</option>{"".join(f"<option>{html.unescape(r)}</option>" for r,_,_ in roles)}<option>Other / open application</option></select></div><div class="field"><label for="j-loc">City / state</label><input id="j-loc" type="text" name="location"></div></div>
 <div class="field"><label for="j-port">Portfolio or LinkedIn link</label><input id="j-port" type="url" name="portfolio" placeholder="https://"></div>
 <div class="field"><label for="j-why">Tell us about your work and local knowledge</label><textarea id="j-why" name="message" required></textarea></div>
 <button class="btn btn-primary" type="submit" style="color:#fff">Send application</button><p class="form-status" role="status" aria-live="polite"></p></form></div></section>'''
    page("careers/index.html", "Careers at 66223.com — writers, photographers, sales", "Open roles at 66223.com: local writers, photographers, video creators, sponsorship reps, community coordinators and web developers.", body, current="community/", priority="0.5")

# ----------------------------------------------------------------- advertise, list business
def build_business():
    tiers = [("Featured Pro","$99","/mo",["Featured card in one service category","Priority in matched requests for that category","“Featured” badge, clearly labeled"],False),
             ("Category Sponsor","$249","/mo",["Exclusive sponsor of one guide category","Logo + 50-word message on every guide in it","Monthly performance report"],True),
             ("Homepage Partner","$499","/mo",["Labeled partner block on the homepage","Category sponsorship included","Newsletter mention each month"],False),
             ("Contest Title Sponsor","$750","/season",["“Presented by” naming on a contest season","Fund and present the prizes","Logo on rules, entries and winner posts"],False)]
    tc = "".join(f'<div class="card tier reveal{" featured" if f else ""}">{"<span class=badge>Best value</span>" if f else ""}<span class="tag">{n}</span><div class="price">{p}<small>{u}</small></div><ul>{"".join(f"<li>{x}</li>" for x in li)}</ul><a class="btn {"btn-gold" if f else "btn-ghost"} btn-block" href="#adv-form">Request this</a></div>' for n,p,u,li,f in tiers)
    body = page_hero("Advertise", "Reach people deciding where to live, buy and hire in 66223", "Our readers are relocating, buying, selling and fixing homes in one of the Kansas City metro's highest-income ZIP codes. Sponsorships are always clearly labeled — that's why they work.", [("advertise/","Advertise")]) + f'''
<section class="section-tight"><div class="wrap grid g4">{tc}</div><p class="kicker wrap" style="margin-top:12px">Introductory rates. Custom packages, lead-based pricing and multi-ZIP campaigns available. Domain purchase or strategic partnership? <a href="{INQUIRY_URL}" target="_blank" rel="noopener">Contact here</a>.</p></section>
<section class="section-tight"><div class="wrap grid g3">
 <div class="card">{icon("users")}<h3>The audience</h3><p>Median household income in 66223 is about $113,700 and the median home value about $437,500 (2024). Overland Park ranks #2 nationally for raising a family (WalletHub 2026).</p></div>
 <div class="card">{icon("shield")}<h3>Our standards</h3><p>We label every sponsored placement, never sell editorial verdicts, and only accept licensed, insured pros in regulated trades.</p></div>
 <div class="card">{icon("chart")}<h3>Pay for results</h3><p>Prefer performance? Ask about exclusive per-lead pricing for buyer, seller, mortgage and roofing requests.</p></div>
</div></section>
<section class="section-tight" id="adv-form"><div class="wrap"><form class="form form-card" data-form="Advertising / sponsorship inquiry" data-success="Thanks — we'll send availability and a media kit within one business day." style="max-width:820px">{HP}
 <h2>Request availability &amp; media kit</h2>
 <div class="row2"><div class="field"><label for="a-name">Name</label><input id="a-name" type="text" name="name" required></div><div class="field"><label for="a-co">Company</label><input id="a-co" type="text" name="company" required></div></div>
 <div class="row2"><div class="field"><label for="a-email">Work email</label><input id="a-email" type="email" name="email" required></div><div class="field"><label for="a-phone">Phone</label><input id="a-phone" type="tel" name="phone"></div></div>
 <div class="row2"><div class="field"><label for="a-pkg">Interested in</label><select id="a-pkg" name="package"><option>Featured Pro</option><option>Category Sponsor</option><option>Homepage Partner</option><option>Contest Title Sponsor</option><option>Pay-per-lead</option><option>Domain / website acquisition</option><option>Strategic partnership</option></select></div>
 <div class="field"><label for="a-budget">Monthly budget</label><select id="a-budget" name="budget"><option>Under $250</option><option>$250–$750</option><option>$750–$2,000</option><option>$2,000+</option></select></div></div>
 <div class="field"><label for="a-msg">Goals</label><textarea id="a-msg" name="message"></textarea></div>
 <button class="btn btn-primary" type="submit" style="color:#fff">Send inquiry</button><p class="form-status" role="status" aria-live="polite"></p></form></div></section>'''
    page("advertise/index.html", "Advertise on 66223.com — sponsorships & local leads", "Sponsorship packages and pay-per-lead options to reach movers, buyers, sellers and homeowners in 66223, Overland Park, Kansas.", body, current="advertise/", priority="0.7")

    body = page_hero("For local pros", "Get matched with 66223 customers", "Join the network that receives buyer, seller, mortgage, moving and home-service requests from south Overland Park.", [("advertise/","Advertise"),("","List your business")]) + f'''
<section class="section-tight"><div class="wrap grid g2" style="align-items:start">
<div class="prose"><h2>Who we're looking for</h2><ul><li>Real estate agents and teams active in 66223 and neighboring ZIPs</li><li>Mortgage lenders and insurance agents licensed in Kansas</li><li>Movers, roofers, HVAC, plumbing, electrical, lawn and handyman pros serving Johnson County</li></ul>
<h2>What you get</h2><ul><li>Requests from people who asked to be contacted, with consent recorded</li><li>No more than three pros per request</li><li>Optional Featured Pro placement and category sponsorships</li></ul>
<div class="callout"><strong>Standards:</strong> Applicable licenses and insurance required for regulated trades. We remove pros who don't respond quickly or receive repeated complaints.</div></div>
<form class="form form-card" data-form="Pro network application" data-success="Application received — we'll be in touch within two business days.">{HP}
 <h3>Apply to join</h3>
 <div class="field"><label for="p-biz">Business name</label><input id="p-biz" type="text" name="business" required></div>
 <div class="row2"><div class="field"><label for="p-cat">Category</label><select id="p-cat" name="category" required><option value="">Choose…</option><option>Real estate agent</option><option>Mortgage lender</option><option>Insurance</option><option>Moving</option><option>Roofing</option><option>HVAC</option><option>Plumbing</option><option>Electrical</option><option>Lawn / landscaping</option><option>Handyman / remodel</option><option>Other</option></select></div>
 <div class="field"><label for="p-web">Website</label><input id="p-web" type="url" name="website" placeholder="https://"></div></div>
 <div class="row2"><div class="field"><label for="p-name">Contact name</label><input id="p-name" type="text" name="name" required></div><div class="field"><label for="p-phone">Phone</label><input id="p-phone" type="tel" name="phone" required></div></div>
 <div class="field"><label for="p-email">Email</label><input id="p-email" type="email" name="email" required></div>
 <div class="field"><label for="p-lic">License # (if applicable)</label><input id="p-lic" type="text" name="license"></div>
 <div class="field"><label for="p-vol">Leads you can handle per month</label><select id="p-vol" name="capacity"><option>1–5</option><option>6–15</option><option>16–40</option><option>40+</option></select></div>
 <button class="btn btn-primary" type="submit" style="color:#fff">Apply now</button><p class="form-status" role="status" aria-live="polite"></p></form>
</div></section>'''
    page("list-your-business/index.html", "List your business — join the 66223 pro network", "Local agents, lenders, movers and home-service pros: apply to receive customer requests from 66223 and Overland Park.", body, current="advertise/", priority="0.6")

# ----------------------------------------------------------------- company & legal
def legal(path, title, desc, h1, inner, crumb):
    body = page_hero("Policy" if "policy" in path or "terms" in path or "disclaimer" in path else "About", h1, f"Last updated {datetime.date.today().strftime('%B %d, %Y')}.", [(path.replace('index.html',''), crumb)]) + f'<section class="section-tight"><div class="wrap prose">{inner}</div></section>'
    page(path, title, desc, body, priority="0.3")

def build_company():
    about = f'''<p class="lead">66223.com is an independent, people-first guide to ZIP 66223 — the southern part of Overland Park, Kansas. We help newcomers decide whether to move here, help residents make better money decisions about their homes, and connect people with trustworthy local pros.</p>
<h2>What we publish</h2><ul><li><strong>Guides</strong> — practical, sourced explainers on moving, property taxes, buying and selling, home maintenance, schools and family life.</li><li><strong>Calculators</strong> — mortgage, Kansas property tax, affordability, rent vs. buy, moving cost and cost of living, preloaded with local data.</li><li><strong>Data</strong> — a sourced snapshot of 66223 we keep updated.</li><li><strong>Community programs</strong> — contests, pro nominations and local talent opportunities.</li></ul>
<h2>How we make money</h2><p>We show advertising served by Google AdSense, offer clearly labeled sponsorships, and may receive referral fees when we connect a reader with a local professional at the reader's request. Reader contributions support operations. None of this changes what we write; see our <a href="{{{{root}}}}editorial-policy/">editorial policy</a>.</p>
<h2>Independence</h2><p>We are not affiliated with the City of Overland Park, Johnson County, the U.S. Postal Service, Blue Valley USD 229, or any business mentioned on this site.</p>
<h2>Contact</h2><p>Questions, corrections or partnership ideas? Use our <a href="{{{{root}}}}contact/">contact page</a>. Interested in this website or domain name? <a href="{INQUIRY_URL}" target="_blank" rel="noopener">Contact here</a>.</p>'''
    legal("about/index.html","About 66223.com","About 66223.com, an independent guide to living, moving and owning a home in ZIP 66223, Overland Park, Kansas.","About 66223.com",about,"About")

    ed = '''<h2>Accuracy</h2><p>Every statistic we publish links to, or names, a public source. When sources disagree, we say so. We review guides at least twice a year and when rules change. Numbers we can't verify are presented as clearly labeled rules of thumb or examples.</p>
<h2>Independence</h2><p>Advertisers and sponsors cannot buy coverage, rankings or edits. Sponsored content is labeled “Sponsored” or “Partner”. Referral relationships never determine what a guide recommends.</p>
<h2>Not professional advice</h2><p>We explain how things work so you can ask better questions. For legal, tax, lending, insurance or real-estate decisions, consult a licensed professional.</p>
<h2>Corrections</h2><p>Spot an error? Tell us through the contact page. We correct material errors promptly and note significant updates on the page.</p>
<h2>Third-party content</h2><p>We embed YouTube videos created by others with credit and our own commentary. Creators can request removal at any time.</p>'''
    legal("editorial-policy/index.html","Editorial policy","How 66223.com researches, sources, corrects and separates editorial content from advertising.","Editorial policy",ed,"Editorial policy")

    priv = '''<p>This policy explains what information 66223.com (“we”, “us”) collects, how we use it, and your choices.</p>
<h2>Information you give us</h2><p>When you submit a form (matching requests, contest entries, applications, newsletter, sponsorship or support inquiries) we collect what you enter — such as name, email, phone, ZIP and details of your request. Form submissions are delivered to us through a third-party form-processing service (FormSubmit) and stored in our email system.</p>
<h2>How we use it</h2><ul><li>To respond to you and provide what you asked for.</li><li>For matching requests: to share your request with up to three relevant local professionals, <strong>only when you give consent</strong> on the form.</li><li>To run contests and contact winners.</li><li>To send the newsletter if you subscribe (unsubscribe anytime).</li></ul><p>We do not sell your personal information to data brokers or list sellers.</p>
<h2>Advertising and cookies (Google AdSense)</h2><p>We use Google AdSense to show ads. Third-party vendors, including Google, use cookies to serve ads based on your prior visits to this and other websites. Google's use of advertising cookies enables it and its partners to serve ads to you based on your visits to this site and/or other sites on the internet. You may opt out of personalized advertising by visiting <a href="https://www.google.com/settings/ads" target="_blank" rel="noopener">Google Ads Settings</a>, or opt out of some third-party vendors' use of cookies for personalized advertising at <a href="https://www.aboutads.info/choices/" target="_blank" rel="noopener">www.aboutads.info</a>. Learn how Google uses information from sites that use its services at <a href="https://policies.google.com/technologies/partner-sites" target="_blank" rel="noopener">policies.google.com/technologies/partner-sites</a>.</p>
<p>Visitors in the EEA, UK and Switzerland will be shown a consent message managed through Google's certified consent tools before personalized ads are served.</p>
<h2>Other cookies and storage</h2><p>We store small preferences in your browser (theme, cookie choice). Embedded YouTube videos load only when you click play and use YouTube's privacy-enhanced mode; YouTube's own policies then apply. Fonts are served by Google Fonts.</p>
<h2>Your choices and rights</h2><p>You may ask us to access, correct or delete personal information you submitted, or to stop contacting you, through the <a href="{{root}}contact/">contact page</a>. Residents of states with privacy laws (such as California) may have additional rights, including to know and delete information and to opt out of “sale” or “sharing”; we honor these requests.</p>
<h2>Children</h2><p>This site is intended for adults. We do not knowingly collect information from children under 13, and contests are limited to people 18 and older.</p>
<h2>Retention and security</h2><p>We keep form submissions only as long as needed for the purpose collected or as required by law, and use reasonable safeguards. No method of transmission is perfectly secure.</p>
<h2>Changes</h2><p>We will post updates here with a new “last updated” date.</p>'''
    legal("privacy/index.html","Privacy & cookie policy","How 66223.com collects and uses information, Google AdSense cookies, consent choices and your privacy rights.","Privacy &amp; cookie policy",priv,"Privacy")

    terms = '''<h2>Acceptance</h2><p>By using 66223.com you agree to these terms. If you don't agree, please don't use the site.</p>
<h2>Information only</h2><p>Content and calculators are general information and estimates, not legal, tax, financial, insurance or real-estate advice, and not an offer of credit or insurance. Verify figures with official sources and licensed professionals before acting.</p>
<h2>Matching service</h2><p>When you request a match, we pass your request to independent professionals. They are not our employees or agents. We don't guarantee their availability, pricing or work quality; do your own due diligence, including checking licenses and insurance.</p>
<h2>User submissions</h2><p>You're responsible for what you submit. Don't submit unlawful, infringing or misleading content. Contest entries are also governed by the contest's official rules.</p>
<h2>Intellectual property</h2><p>Original text, design, code and tools on this site are owned by the publisher of 66223.com. You may share links and short quotations with attribution. Third-party names, logos and videos belong to their owners.</p>
<h2>External links</h2><p>We link to other websites for convenience; we're not responsible for their content or practices.</p>
<h2>Limitation of liability</h2><p>To the fullest extent permitted by law, the site is provided “as is”, and we are not liable for indirect or consequential damages arising from your use of it.</p>
<h2>Changes</h2><p>We may update these terms; continued use means you accept the updated terms. Governing law: the State of Kansas, without regard to conflict-of-law rules.</p>'''
    legal("terms/index.html","Terms of use","Terms of use for 66223.com, including information-only content, the matching service, submissions and intellectual property.","Terms of use",terms,"Terms")

    disc = f'''<h2>Trademark disclosure</h2><p>66223.com uses the number “66223” solely in its ordinary, descriptive sense — as the United States Postal Service ZIP Code that identifies part of Overland Park, Kansas. <strong>No trademark, service mark or exclusive right is claimed in the number “66223”</strong>, and nothing on this site suggests that any government body, postal service, school district or business sponsors or endorses us.</p>
<p>“ZIP Code” is a registered trademark of the United States Postal Service. “Overland Park”, “Johnson County”, “Blue Valley” and the names of attractions, businesses, publications and platforms mentioned on this site are used for identification only and belong to their respective owners. Mention does not imply affiliation or endorsement.</p>
<h2>Copyright disclosure</h2><p>All original articles, data presentation, calculators, code and site design are &copy; {datetime.date.today().year} the publisher of 66223.com. Statistics are drawn from public sources (U.S. Census Bureau, American Community Survey and the publishers credited on each page); facts themselves aren't owned, and we credit the compilations we rely on. Embedded videos remain the property of their creators and are displayed through YouTube's official embed player. If you believe any material on this site infringes your rights, contact us via the <a href="{{{{root}}}}contact/">contact page</a> with the URL and details, and we'll respond promptly.</p>
<h2>Advertising &amp; affiliate disclosure</h2><p>This site displays ads served by Google AdSense and may publish labeled sponsorships. We may earn referral fees when a reader asks to be connected with a local professional. This compensation does not influence our editorial content.</p>
<h2>No professional advice</h2><p>Information and calculator results are estimates for education only. Always confirm with official sources (Johnson County, the City of Overland Park, the Kansas Department of Revenue, your school district) and licensed professionals.</p>
<h2>Domain inquiries</h2><p>Interested in acquiring or partnering on this website or the 66223.com domain name? <a href="{INQUIRY_URL}" target="_blank" rel="noopener">Contact here</a>.</p>'''
    legal("disclaimer/index.html","Disclaimer, trademark & copyright disclosure","Trademark and copyright disclosure for 66223.com: descriptive use of the ZIP code 66223, third-party marks, advertising and affiliate disclosure.","Disclaimer, trademark &amp; copyright disclosure",disc,"Disclaimer")

    body = page_hero("Contact", "Contact 66223.com", "Questions, corrections, partnership ideas or press — send us a note. We reply within two business days.", [("contact/","Contact")]) + f'''
<section class="section-tight"><div class="wrap grid g2" style="align-items:start">
<form class="form form-card" data-form="General contact" data-success="Message sent. We'll reply within two business days.">{HP}
 <div class="row2"><div class="field"><label for="ct-name">Name</label><input id="ct-name" type="text" name="name" required autocomplete="name"></div><div class="field"><label for="ct-email">Email</label><input id="ct-email" type="email" name="email" required autocomplete="email"></div></div>
 <div class="field"><label for="ct-topic">Topic</label><select id="ct-topic" name="topic"><option>General question</option><option>Correction</option><option>Advertising / sponsorship</option><option>Partnership</option><option>Website / domain acquisition</option><option>Press</option><option>Creator / content removal</option><option>Privacy request</option></select></div>
 <div class="field"><label for="ct-msg">Message</label><textarea id="ct-msg" name="message" required></textarea></div>
 <button class="btn btn-primary" type="submit" style="color:#fff">Send message</button><p class="form-status" role="status" aria-live="polite"></p></form>
<div class="grid" style="gap:16px">
 <div class="card">{icon("mail")}<h3>Prefer email?</h3><p>Click below to open a new message in your email app.</p><a class="btn btn-ghost" href="#" data-contact="Inquiry from 66223.com">Email us</a></div>
 <div class="card">{icon("brief")}<h3>Domain, sponsorship &amp; partnerships</h3><p>Interested in this website, the domain name, sponsorship, advertising or partnership?</p><a class="btn btn-gold" href="{INQUIRY_URL}" target="_blank" rel="noopener">Contact here</a></div>
 <div class="card">{icon("users")}<h3>Need a local pro?</h3><p>Use our free matching form for the fastest response.</p><a class="btn btn-primary" href="{{{{root}}}}get-matched/" style="color:#fff">Get matched</a></div>
</div></div></section>'''
    page("contact/index.html", "Contact 66223.com", "Contact 66223.com for questions, corrections, advertising, partnerships or domain inquiries.", body, priority="0.5")

# ----------------------------------------------------------------- home
def build_home(guides):
    feat = [g for g in guides if g["slug"] in ("moving-to-overland-park-66223","property-taxes-johnson-county-kansas","cost-of-living-66223","buying-a-home-in-66223","hail-storm-roof-insurance-kansas","family-things-to-do-overland-park")]
    body = f'''<section class="hero"><div class="wrap hero-grid">
<div>
 <span class="eyebrow">ZIP 66223 · South Overland Park, Kansas</span>
 <h1>Move smarter. Own smarter. Live better in 66223.</h1>
 <p class="lead">The independent guide to one of America's top-ranked suburbs — with real local numbers, Kansas-specific calculators and free matching with pros who work here.</p>
 <div class="hero-actions"><a class="btn btn-primary" href="{{{{root}}}}get-matched/" style="color:#fff">Get matched with a local pro</a><a class="btn btn-ghost" href="{{{{root}}}}guides/moving-to-overland-park-66223/">Read the moving guide</a></div>
 <div class="trust-row"><span>Free &amp; independent</span><span>Every stat sourced</span><span>Kansas tax rules built in</span></div>
</div>
<div class="card" style="padding:28px">
 <div class="numerals" aria-label="66 22 3"><span>66</span><span>22</span><span>3</span></div>
 <p style="margin:14px 0 18px;color:var(--ink-2)">One ZIP. Twenty-five thousand neighbors. One of the metro's strongest housing markets.</p>
 <div class="grid g2" style="gap:12px">
  <div class="stat" style="padding:0"><b>$113.7k</b><span>Median household income</span></div>
  <div class="stat" style="padding:0"><b>$437.5k</b><span>Median home value (2024)</span></div>
  <div class="stat" style="padding:0"><b>#2</b><span>US city to raise a family*</span></div>
  <div class="stat" style="padding:0"><b>14.5</b><span>City mills — lowest in JoCo</span></div></div>
 <p class="src" style="margin:12px 0 0">*Overland Park, WalletHub 2026. See <a href="{{{{root}}}}data/">sources</a>.</p>
</div></div></section>

<section class="section-tight"><div class="wrap">
 <div class="section-head"><div><h2>What brings you to 66223?</h2><p>Pick your path — we'll point you to the right guide, tool and pro.</p></div></div>
 <div class="grid g4">
  <a class="card card-link reveal" href="{{{{root}}}}get-matched/?goal=relocate">{icon("map")}<h3>I'm moving here</h3><p>Costs, neighborhoods, schools and a first-90-days plan.</p><span class="more">Start &rarr;</span></a>
  <a class="card card-link reveal" href="{{{{root}}}}get-matched/?goal=buy">{icon("key")}<h3>I'm buying</h3><p>Affordability, taxes, inspections and agents who know the area.</p><span class="more">Start &rarr;</span></a>
  <a class="card card-link reveal" href="{{{{root}}}}get-matched/?goal=sell">{icon("home")}<h3>I'm selling</h3><p>Pricing, prep and net-proceeds math for 66223.</p><span class="more">Start &rarr;</span></a>
  <a class="card card-link reveal" href="{{{{root}}}}get-matched/?goal=services">{icon("tool")}<h3>I need a home pro</h3><p>Roofing, HVAC, lawn and storm repairs from local pros.</p><span class="more">Start &rarr;</span></a>
 </div></div></section>

<section class="section section-alt"><div class="wrap">
 <div class="section-head"><div><h2>Free calculators, built for Kansas</h2><p>The 11.5% assessment rule and the $75,000 school-levy exemption are built in, with 66223 medians as defaults.</p></div><a class="btn btn-ghost" href="{{{{root}}}}tools/">All calculators</a></div>
 <div class="grid g3">{"".join(tool_card(t) for t in TOOLS)}</div>
</div></section>

<section class="section"><div class="wrap">
 <div class="section-head"><div><h2>Most-read guides</h2><p>Original, practical and sourced — the questions people actually ask before moving or buying here.</p></div><a class="btn btn-ghost" href="{{{{root}}}}guides/">All guides</a></div>
 <div class="grid g3">{"".join(guide_card(g) for g in feat)}</div>
</div></section>

<section class="section-tight"><div class="wrap">{quick_lead(source="home")}</div></section>

<section class="section"><div class="wrap">
 <div class="section-head"><div><h2>See it before you move</h2><p>Hand-picked videos on life in Overland Park — tours, honest pros and cons, and family favorites.</p></div><a class="btn btn-ghost" href="{{{{root}}}}videos/">All videos</a></div>
 <div class="grid g3">{"".join(video_card(*v[:2], v[2], v[3]) for v in [VIDEOS[0], VIDEOS[6], VIDEOS[8]])}</div>
</div></section>

<section class="section section-alt"><div class="wrap grid g3">
 <a class="card card-link reveal" href="{{{{root}}}}contests/">{icon("trophy")}<span class="tag">Contest open</span><h3>66223 in Focus</h3><p>Free photo contest with $250, $100 and $50 gift-card prizes. Entries close Jan 31, 2027.</p><span class="more">Enter now &rarr;</span></a>
 <a class="card card-link reveal" href="{{{{root}}}}donate/">{icon("heart")}<span class="tag">Support</span><h3>Keep it free</h3><p>Fund research, local talent and prizes — from $5.</p><span class="more">Support us &rarr;</span></a>
 <a class="card card-link reveal" href="{{{{root}}}}advertise/">{icon("mega")}<span class="tag">For businesses</span><h3>Advertise &amp; sponsor</h3><p>Reach movers, buyers and homeowners in a $113k-median-income ZIP.</p><span class="more">See packages &rarr;</span></a>
</div></section>

<section class="section"><div class="wrap prose" style="max-width:860px">
 <h2>Why 66223?</h2>
 <p>ZIP 66223 covers part of southern Overland Park in Johnson County, Kansas — a suburban corner of the Kansas City metro that keeps showing up on national lists. Niche named Overland Park the #10 best city to live in America for 2026, and WalletHub ranked it the #2 place in the country to raise a family. Inside the ZIP, roughly 25,000 people live in about 9,800 households, the median household income is around $113,700, and about two-thirds of adults hold a bachelor's degree or higher.</p>
 <p>Those numbers come with real decisions attached: how much house to buy when values have risen from about $263,000 in 2011 to about $437,500, how Kansas property taxes actually work, whether to rent first, which school boundary a specific address falls in, and how to protect a roof in hail country. 66223.com exists to answer those questions clearly — and to connect you with people who can help when you're ready.</p>
 <p class="src">Sources: U.S. Census 2020, ACS 2023, Niche 2026, WalletHub 2026, zip-codes.com. Full list on the <a href="{{{{root}}}}data/">data page</a>.</p>
</div></section>'''
    page("index.html", "66223 — Overland Park living, moving & home-money guide", "Independent guide to ZIP 66223, south Overland Park, Kansas: moving guides, Kansas property tax and mortgage calculators, local data and free matching with local pros.", body, current="", priority="1.0",
         schema=[{"@context":"https://schema.org","@type":"Organization","name":"66223.com","url":SITE_URL,"logo":SITE_URL+"assets/img/favicon.svg"}])

# ----------------------------------------------------------------- static files
def build_static():
    # sitemap.html
    groups = {}
    for p,t,_ in PAGES:
        k = p.split("/")[0] if "/" in p else "main"
        groups.setdefault(k, []).append((p,t))
    lis = "".join(f'<li><a href="{{{{root}}}}{p.replace("index.html","")}">{e(t)}</a></li>' for p,t,_ in sorted(PAGES))
    page("sitemap.html", "Sitemap", "All pages on 66223.com.", page_hero("Sitemap","All pages","Every guide, tool and page on 66223.com.") + f'<section class="section-tight"><div class="wrap prose"><ul>{lis}</ul></div></section>', priority="0.3")
    page("404.html", "Page not found", "This page doesn't exist.", page_hero("404","We couldn't find that page","It may have moved. Try the guides, the calculators, or head home.") + '<section class="section-tight"><div class="wrap"><a class="btn btn-primary" href="/" style="color:#fff">Go home</a> <a class="btn btn-ghost" href="/66223-com/">Home (preview URL)</a></div></section>', noindex=True)
    with open(os.path.join(OUT,"sitemap.xml"),"w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for p,t,pr in sorted(PAGES, key=lambda x:-float(x[2])):
            loc = SITE_URL + ("" if p=="index.html" else p.replace("index.html",""))
            f.write(f"  <url><loc>{loc}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>\n")
        f.write("</urlset>\n")
    with open(os.path.join(OUT,"robots.txt"),"w") as f: f.write(f"User-agent: *\nAllow: /\n\nUser-agent: Mediapartners-Google\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n")
    with open(os.path.join(OUT,"ads.txt"),"w") as f: f.write("google.com, pub-6620975821265271, DIRECT, f08c47fec0942fa0\n")
    open(os.path.join(OUT,".nojekyll"),"w").close()
    cname = os.environ.get("CNAME")
    if cname:
        with open(os.path.join(OUT,"CNAME"),"w") as f: f.write(cname.strip()+"\n")

def main():
    if os.path.exists(OUT):
        for n in os.listdir(OUT):
            if n in (".git", ".github", "_source", "README.md", "BUILD-PROMPTS.md"): continue
            fp = os.path.join(OUT, n)
            shutil.rmtree(fp) if os.path.isdir(fp) else os.remove(fp)
    os.makedirs(OUT, exist_ok=True)
    shutil.copytree(os.path.join(SRC,"assets"), os.path.join(OUT,"assets"))
    guides = load_guides()
    build_home(guides); build_guides(guides); build_tools(); build_get_matched(); build_data(); build_videos()
    build_community(); build_business(); build_company(); build_static()
    print(f"Built {len(PAGES)} indexable pages -> {OUT}  (SITE_URL={SITE_URL})")

if __name__ == "__main__":
    main()
