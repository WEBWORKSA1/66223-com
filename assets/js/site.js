/* 66223.com — site behaviour. No email address appears in plain text anywhere on this site. */
(function () {
  "use strict";

  /* ---------- Optional payment links (fill in to show direct donate buttons) ---------- */
  var PAY = {
    paypal: "",      // e.g. "https://www.paypal.com/donate/?hosted_button_id=XXXX"
    stripe: "",      // e.g. "https://donate.stripe.com/XXXX"
    bmac: ""         // e.g. "https://www.buymeacoffee.com/XXXX"
  };

  /* ---------- Contact routing (obfuscated; assembled only at send time) ---------- */
  function route() {
    var p = ["d2Vid29ya3NhMQ==", "Z21haWwuY29t"];
    try { return atob(p[0]) + String.fromCharCode(64) + atob(p[1]); } catch (e) { return ""; }
  }

  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ---------- Theme ---------- */
  var root = document.documentElement;
  try { var saved = localStorage.getItem("theme"); if (saved) root.setAttribute("data-theme", saved); } catch (e) {}
  $$("[data-theme-toggle]").forEach(function (b) {
    b.addEventListener("click", function () {
      var cur = root.getAttribute("data-theme");
      var dark = cur ? cur === "dark" : window.matchMedia("(prefers-color-scheme: dark)").matches;
      var next = dark ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) {}
    });
  });

  /* ---------- Mobile menu ---------- */
  var mb = $(".menu-btn"), nl = $(".nav-links");
  if (mb && nl) mb.addEventListener("click", function () {
    var o = nl.classList.toggle("open"); mb.setAttribute("aria-expanded", o ? "true" : "false");
  });

  /* ---------- Reveal on scroll ---------- */
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } }); }, { rootMargin: "0px 0px -8% 0px" });
    $$(".reveal").forEach(function (el) { io.observe(el); });
  } else { $$(".reveal").forEach(function (el) { el.classList.add("in"); }); }

  /* ---------- Cookie notice ---------- */
  var ck = $(".cookie");
  try { if (ck && !localStorage.getItem("cookie-ok")) ck.classList.add("show"); } catch (e) { if (ck) ck.classList.add("show"); }
  $$("[data-cookie]").forEach(function (b) { b.addEventListener("click", function () {
    try { localStorage.setItem("cookie-ok", b.getAttribute("data-cookie")); } catch (e) {}
    ck.classList.remove("show");
  }); });

  /* ---------- Mobile sticky CTA hides near forms ---------- */
  var mc = $(".mobile-cta");
  if (mc && "IntersectionObserver" in window) {
    var forms = $$("form");
    var vis = 0;
    var fo = new IntersectionObserver(function (es) { es.forEach(function (e) { vis += e.isIntersecting ? 1 : -1; }); mc.classList.toggle("hide", vis > 0); });
    forms.forEach(function (f) { fo.observe(f); });
  }

  /* ---------- YouTube facade ---------- */
  $$(".video[data-id]").forEach(function (v) {
    function load() {
      if (v.querySelector("iframe")) return;
      var f = document.createElement("iframe");
      f.src = "https://www.youtube-nocookie.com/embed/" + v.getAttribute("data-id") + "?autoplay=1&rel=0";
      f.title = v.getAttribute("data-title") || "YouTube video";
      f.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
      f.allowFullscreen = true;
      v.innerHTML = ""; v.appendChild(f);
    }
    v.addEventListener("click", load);
    v.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); load(); } });
  });

  /* ---------- Contact links (hidden address) ---------- */
  $$("[data-contact]").forEach(function (a) {
    a.addEventListener("click", function (e) {
      e.preventDefault();
      var subj = a.getAttribute("data-contact") || "Inquiry from 66223.com";
      window.location.href = "mailto:" + route() + "?subject=" + encodeURIComponent(subj);
    });
  });

  /* ---------- Forms ---------- */
  function serialize(form) {
    var data = {};
    $$("input,select,textarea", form).forEach(function (el) {
      if (!el.name || el.type === "submit" || el.name === "_hp") return;
      if ((el.type === "checkbox" || el.type === "radio") && !el.checked) return;
      if (data[el.name]) data[el.name] += ", " + el.value; else data[el.name] = el.value;
    });
    data["_page"] = location.href;
    data["_submitted"] = new Date().toISOString();
    return data;
  }
  function mailtoFallback(subject, data) {
    var body = Object.keys(data).map(function (k) { return k + ": " + data[k]; }).join("\n");
    window.location.href = "mailto:" + route() + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
  }
  $$("form[data-form]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var status = $(".form-status", form);
      var hp = form.querySelector("[name=_hp]");
      if (hp && hp.value) return; // bot
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var kind = form.getAttribute("data-form");
      var subject = "66223.com — " + kind;
      var data = serialize(form);
      data["_subject"] = subject; data["_template"] = "table"; data["_captcha"] = "false";
      var btn = form.querySelector("[type=submit]");
      if (btn) { btn.disabled = true; btn.dataset.label = btn.textContent; btn.textContent = "Sending…"; }
      if (status) { status.className = "form-status"; status.textContent = ""; }
      fetch("https://formsubmit.co/ajax/" + route(), {
        method: "POST", headers: { "Content-Type": "application/json", "Accept": "application/json" }, body: JSON.stringify(data)
      }).then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (res) {
          if (res.ok && (res.j.success === true || res.j.success === "true")) {
            var done = form.getAttribute("data-success") || "Thanks — we received your request and will be in touch shortly.";
            if (status) { status.className = "form-status ok"; status.textContent = done; }
            form.reset();
            var show = form.getAttribute("data-reveal"); if (show && $(show)) $(show).classList.remove("hidden");
            if (form.classList.contains("multistep")) goStep(form, 0);
            try { if (window.gtag) gtag("event", "generate_lead", { form: kind }); } catch (e) {}
          } else { throw new Error("relay"); }
        })
        .catch(function () {
          if (status) { status.className = "form-status err"; status.textContent = "Opening your email app to finish sending…"; }
          mailtoFallback(subject, data);
        })
        .finally(function () { if (btn) { btn.disabled = false; btn.textContent = btn.dataset.label; } });
    });
  });

  /* ---------- Multi-step lead form ---------- */
  function goStep(form, n) {
    var steps = $$(".step", form), bars = $$(".steps-bar i", form);
    steps.forEach(function (s, i) { s.classList.toggle("active", i === n); });
    bars.forEach(function (b, i) { b.classList.toggle("on", i <= n); });
    form.dataset.step = n;
    var focus = steps[n] && steps[n].querySelector("input,select,textarea"); if (focus && n > 0) focus.focus({ preventScroll: true });
  }
  $$("form.multistep").forEach(function (form) {
    goStep(form, 0);
    form.addEventListener("click", function (e) {
      var t = e.target.closest("[data-next],[data-prev]"); if (!t) return;
      e.preventDefault();
      var n = +form.dataset.step;
      if (t.hasAttribute("data-next")) {
        var cur = $$(".step", form)[n];
        var bad = $$("input,select,textarea", cur).filter(function (el) { return !el.checkValidity(); })[0];
        if (bad) { bad.reportValidity(); return; }
        goStep(form, n + 1);
      } else goStep(form, Math.max(0, n - 1));
    });
    // conditional detail blocks
    $$("[name=goal]", form).forEach(function (r) { r.addEventListener("change", function () {
      $$("[data-goal]", form).forEach(function (b) {
        var on = b.getAttribute("data-goal").split(" ").indexOf(r.value) > -1;
        b.classList.toggle("hidden", !on);
        $$("select,input", b).forEach(function (el) { el.disabled = !on; });
      });
    }); });
    // preselect from URL ?goal=
    var g = new URLSearchParams(location.search).get("goal");
    if (g) { var el = form.querySelector("[name=goal][value='" + g + "']"); if (el) { el.checked = true; el.dispatchEvent(new Event("change")); } }
  });

  /* ---------- Donation amount + direct links ---------- */
  $$("[data-amount]").forEach(function (r) { r.addEventListener("change", function () {
    var out = $("#donate-amount"); if (out) out.value = r.value === "custom" ? "" : r.value;
    var c = $("#custom-amount-wrap"); if (c) c.classList.toggle("hidden", r.value !== "custom");
  }); });
  var payBox = $("#pay-direct");
  if (payBox) {
    var html = "";
    if (PAY.paypal) html += '<a class="btn btn-gold" rel="noopener" target="_blank" href="' + PAY.paypal + '">Give with PayPal</a>';
    if (PAY.stripe) html += '<a class="btn btn-primary" rel="noopener" target="_blank" href="' + PAY.stripe + '">Give by card</a>';
    if (PAY.bmac) html += '<a class="btn btn-ghost" rel="noopener" target="_blank" href="' + PAY.bmac + '">Buy us a coffee</a>';
    if (html) { payBox.innerHTML = html; payBox.classList.remove("hidden"); }
  }

  /* ---------- Countdown ---------- */
  $$("[data-countdown]").forEach(function (el) {
    var end = new Date(el.getAttribute("data-countdown")).getTime();
    function tick() {
      var d = Math.max(0, end - Date.now()), s = Math.floor(d / 1000);
      var v = [Math.floor(s / 86400), Math.floor(s % 86400 / 3600), Math.floor(s % 3600 / 60), s % 60];
      $$("b", el).forEach(function (b, i) { b.textContent = String(v[i]).padStart(2, "0"); });
    }
    tick(); setInterval(tick, 1000);
  });

  /* ---------- Guide filter / search ---------- */
  var gq = $("#guide-search");
  function filterGuides() {
    var q = (gq && gq.value || "").toLowerCase();
    var cat = ($(".pill.on[data-cat]") || {}).getAttribute ? $(".pill.on[data-cat]").getAttribute("data-cat") : "all";
    $$("[data-guide]").forEach(function (c) {
      var okc = cat === "all" || c.getAttribute("data-cat") === cat;
      var okq = !q || c.textContent.toLowerCase().indexOf(q) > -1;
      c.classList.toggle("hidden", !(okc && okq));
    });
  }
  if (gq) gq.addEventListener("input", filterGuides);
  $$(".pill[data-cat]").forEach(function (p) { p.addEventListener("click", function () {
    $$(".pill[data-cat]").forEach(function (x) { x.classList.remove("on"); }); p.classList.add("on"); filterGuides();
  }); });

  /* ---------- TOC builder for articles ---------- */
  var toc = $("#toc-list"), prose = $(".prose");
  if (toc && prose) {
    $$("h2", prose).forEach(function (h, i) {
      if (h.closest(".faq")) return;
      if (!h.id) h.id = "s" + (i + 1) + "-" + h.textContent.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 40);
      var li = document.createElement("li"); li.innerHTML = '<a href="#' + h.id + '"></a>'; li.firstChild.textContent = h.textContent; toc.appendChild(li);
    });
  }
  $$(".prose table").forEach(function (t) { if (!t.parentElement.classList.contains("table-scroll")) { var w = document.createElement("div"); w.className = "table-scroll"; t.parentNode.insertBefore(w, t); w.appendChild(t); } });

  /* ---------- Share ---------- */
  $$("[data-share]").forEach(function (b) { b.addEventListener("click", function () {
    if (navigator.share) navigator.share({ title: document.title, url: location.href }).catch(function () {});
    else if (navigator.clipboard) navigator.clipboard.writeText(location.href).then(function () { b.textContent = "Link copied"; });
  }); });

  var y = $("#year"); if (y) y.textContent = new Date().getFullYear();
})();
