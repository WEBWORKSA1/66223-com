#!/usr/bin/env python3
"""Emit 66223.com as a GitHub Pages-native Jekyll site (no Actions needed).
Usage: python3 build_jekyll.py OUT_DIR
Reuses build.py page definitions; writes front-matter pages + _layouts/_includes.
"""
import os, re, sys, json, shutil
import build as B

OUT = os.path.abspath(sys.argv[1])
JPAGES = []
FAQ = {}

def fm_str(s):
    return "'" + str(s).replace("'", "''") + "'"

# --- patch quick_lead to a Jekyll include
_orig_quick_lead = B.quick_lead
def jl_quick_lead(title=None, sub=None, source="quick"):
    return '{% include quick_lead.html source="' + source + '" %}'
B.quick_lead = jl_quick_lead
B.INLINE_CTA = ""  # inline CTA lives inside each guide include

# --- patch page() to write front matter + body
def jpage(path, title, desc, body, current="", depth=None, tool=None, schema=None, priority="0.6", og_type="website", noindex=False):
    full_title = title if title.startswith("66223") else f"{title} | 66223.com"
    ld = [{"@context":"https://schema.org","@type":"WebSite","name":"66223.com","url":"__SITE__","description":B.TAGLINE}] if path=="index.html" else []
    if schema: ld += schema if isinstance(schema, list) else [schema]
    m = re.match(r"guides/([^/]+)/index.html", path)
    pass  # FAQ schema omitted (Google limits FAQ rich results)
    ld_s = json.dumps(ld).replace(B.SITE_URL, "__SITE__") if ld else ""
    fm = ["---", "layout: default", f"title: {fm_str(full_title)}", f"og_title: {fm_str(title)}", f"description: {fm_str(desc)}",
          f"nav: {fm_str(current)}", f"og_type: {og_type}"]
    if tool: fm.append(f"tool: {tool}")
    if noindex: fm.append("noindex: true")
    if path == "404.html": fm.append("permalink: /404.html")
    if ld_s: fm.append(f"ld: {fm_str(ld_s)}")
    fm.append("---")
    doc = "\n".join(fm) + "\n{% assign root = site.baseurl | append: \"/\" %}\n" + body + "\n"
    dest = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, "w", encoding="utf-8").write(doc)
    if not noindex:
        B.PAGES.append((path, title, priority)); JPAGES.append((path, priority))
B.page = jpage

def layout():
    items = [("guides/","Guides"),("tools/","Tools"),("data/","66223 Data"),("videos/","Videos"),("community/","Community"),("advertise/","Advertise")]
    nav = B.nav("{{ root }}", "__NONE__")
    for p,t in items:
        nav = nav.replace(f'<a href="{{{{ root }}}}{p}">{t}</a>', f'<a href="{{{{ root }}}}{p}"{{% if page.nav == "{p}" %}} aria-current="page"{{% endif %}}>{t}</a>')
    foot = B.footer("{{ root }}")
    return f'''{{% assign root = site.baseurl | append: "/" %}}<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{{{ page.title | escape }}}}</title>
<meta name="description" content="{{{{ page.description | escape }}}}">
{{% if page.noindex %}}<meta name="robots" content="noindex">{{% else %}}<meta name="robots" content="index,follow,max-image-preview:large">{{% endif %}}
<link rel="canonical" href="{{{{ site.url }}}}{{{{ site.baseurl }}}}{{{{ page.url | replace: 'index.html', '' }}}}">
<meta property="og:type" content="{{{{ page.og_type | default: 'website' }}}}"><meta property="og:site_name" content="66223.com"><meta property="og:title" content="{{{{ page.og_title | escape }}}}"><meta property="og:description" content="{{{{ page.description | escape }}}}"><meta property="og:url" content="{{{{ site.url }}}}{{{{ site.baseurl }}}}{{{{ page.url | replace: 'index.html', '' }}}}"><meta property="og:image" content="{{{{ site.url }}}}{{{{ site.baseurl }}}}/assets/img/og.svg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#14532d">
<link rel="icon" href="{{{{ root }}}}assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700;9..144,800&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{{{{ root }}}}assets/css/site.css">
{B.ADSENSE}
{{% if page.ld %}}{{% assign site_root = site.url | append: site.baseurl | append: "/" %}}<script type="application/ld+json">{{{{ page.ld | replace: "__SITE__", site_root }}}}</script>{{% endif %}}
</head>
<body{{% if page.tool %}} data-tool="{{{{ page.tool }}}}"{{% endif %}}>
{nav}
<main id="main">
{{{{ content }}}}
</main>
{foot}
<script src="{{{{ root }}}}assets/js/site.js" defer></script>
{{% if page.tool %}}<script src="{{{{ root }}}}assets/js/tools.js" defer></script>{{% endif %}}
</body>
</html>
'''

def main():
    # Safe in-repo rebuild: only replace generated folders, never the whole OUT (it may contain _source/ and .git/)
    os.makedirs(OUT, exist_ok=True)
    for d in ["assets", "_layouts", "_includes"]:
        if os.path.isdir(os.path.join(OUT, d)): shutil.rmtree(os.path.join(OUT, d))
    shutil.copytree(os.path.join(B.SRC,"assets"), os.path.join(OUT,"assets"))
    B.OUT = OUT
    guides = B.load_guides()
    os.makedirs(os.path.join(OUT,"_includes","guides"), exist_ok=True)
    for g in guides:
        faqs = re.findall(r"<summary>(.*?)</summary>\s*<p>(.*?)</p>", g["body"], re.S)
        if faqs:
            FAQ[g["slug"]] = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":re.sub("<.*?>","",q),"acceptedAnswer":{"@type":"Answer","text":re.sub("<.*?>","",a)}} for q,a in faqs]}
        inc = g["body"].replace("<!--CTA-->", "{% include inline_cta.html %}", 1)
        open(os.path.join(OUT,"_includes","guides",g["slug"]+".html"),"w").write(inc + "\n")
        g["body"] = "{% include guides/" + g["slug"] + ".html %}"
    open(os.path.join(OUT,"_includes","quick_lead.html"),"w").write(_orig_quick_lead(source="{{ include.source }}") + "\n")
    open(os.path.join(OUT,"_includes","inline_cta.html"),"w").write('''<aside class="inline-cta"><div><h3>Want a local pro to run your numbers?</h3><p>Free, no-obligation matching with agents, lenders, movers and home pros who work 66223.</p></div><a class="btn btn-primary" href="{{root}}get-matched/" style="color:#fff">Get matched free</a></aside>\n''')
    os.makedirs(os.path.join(OUT,"_layouts"), exist_ok=True)
    open(os.path.join(OUT,"_layouts","default.html"),"w").write(layout())
    B.build_home(guides); B.build_guides(guides); B.build_tools(); B.build_get_matched(); B.build_data(); B.build_videos()
    B.build_community(); B.build_business(); B.build_company()
    # sitemap.html + 404 (via patched page)
    lis = "".join(f'<li><a href="{{{{root}}}}{p.replace("index.html","")}">{B.e(t)}</a></li>' for p,t,_ in sorted(B.PAGES))
    jpage("sitemap.html", "Sitemap", "All pages on 66223.com.", B.page_hero("Sitemap","All pages","Every guide, tool and page on 66223.com.") + f'<section class="section-tight"><div class="wrap prose"><ul>{lis}</ul></div></section>', priority="0.3")
    jpage("404.html", "Page not found", "This page doesn't exist.", B.page_hero("404","We couldn't find that page","It may have moved. Try the guides, the calculators, or head home.") + '<section class="section-tight"><div class="wrap"><a class="btn btn-primary" href="{{root}}" style="color:#fff">Go home</a> <a class="btn btn-ghost" href="{{root}}guides/">Browse guides</a></div></section>', noindex=True)
    urls = "\n".join(f"  <url><loc>{{{{ site.url }}}}{{{{ site.baseurl }}}}/{p.replace('index.html','')}</loc><lastmod>{{{{ site.time | date: '%Y-%m-%d' }}}}</lastmod><priority>{pr}</priority></url>" for p,pr in sorted(JPAGES, key=lambda x:-float(x[1])))
    open(os.path.join(OUT,"sitemap.xml"),"w").write('---\nlayout: null\n---\n<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '\n</urlset>\n')
    open(os.path.join(OUT,"robots.txt"),"w").write("---\nlayout: null\n---\nUser-agent: *\nAllow: /\n\nUser-agent: Mediapartners-Google\nAllow: /\n\nSitemap: {{ site.url }}{{ site.baseurl }}/sitemap.xml\n")
    open(os.path.join(OUT,"ads.txt"),"w").write("google.com, pub-6620975821265271, DIRECT, f08c47fec0942fa0\n")
    cfg_url = os.environ.get("JEKYLL_URL", "https://webworksa1.github.io")
    cfg_base = os.environ.get("JEKYLL_BASEURL", "/66223-com")
    open(os.path.join(OUT,"_config.yml"),"w").write(f'''# 66223.com — GitHub Pages (Jekyll). Pages builds this automatically on every push.
# Custom domain switch: set url to https://66223.com, baseurl to "" and add a CNAME file containing 66223.com.
title: "66223.com"
url: "{cfg_url}"
baseurl: "{cfg_base}"
exclude: [README.md, BUILD-PROMPTS.md, _source]
''')
    print(f"Jekyll source: {len(JPAGES)} indexable pages -> {OUT}")

if __name__ == "__main__":
    main()
