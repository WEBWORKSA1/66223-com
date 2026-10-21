/* 66223.com — calculators. Estimates only. */
(function () {
  "use strict";
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var usd = function (n, d) { if (!isFinite(n)) n = 0; return n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: d == null ? 0 : d }); };
  var num = function (id) { var el = document.getElementById(id); return el ? parseFloat(String(el.value).replace(/[^0-9.\-]/g, "")) || 0 : 0; };
  var set = function (id, v) { var el = document.getElementById(id); if (el) el.textContent = v; };
  var tool = document.body.getAttribute("data-tool");
  function bind(fn) {
    $$("input,select").forEach(function (el) { el.addEventListener("input", fn); el.addEventListener("change", fn); });
    $$(".range-row").forEach(function (r) {
      var range = r.querySelector("input[type=range]"), out = r.querySelector("output");
      if (!range || !out) return;
      var fmt = function () { var f = range.getAttribute("data-fmt"); out.textContent = f === "pct" ? range.value + "%" : f === "yr" ? range.value + " yrs" : f === "num" ? (+range.value).toLocaleString() + " mi" : usd(+range.value); };
      range.addEventListener("input", fmt); fmt();
    });
    fn();
  }
  function pmt(principal, ratePct, years) {
    var r = ratePct / 100 / 12, n = years * 12;
    if (n <= 0) return 0; if (r === 0) return principal / n;
    return principal * r / (1 - Math.pow(1 + r, -n));
  }
  function bar(el, parts) {
    if (!el) return; var total = parts.reduce(function (a, p) { return a + Math.max(0, p[0]); }, 0) || 1;
    el.innerHTML = parts.map(function (p) { return '<i style="width:' + (Math.max(0, p[0]) / total * 100).toFixed(2) + '%;background:' + p[1] + '"></i>'; }).join("");
  }
  /* Kansas property tax: 11.5% residential assessment; $75,000 exemption on statewide 20-mill school levy */
  function ksTax(value, mills) {
    var assessed = value * 0.115;
    var gross = assessed * mills / 1000;
    var credit = Math.min(value, 75000) * 0.115 * 20 / 1000;
    return { assessed: assessed, gross: gross, credit: credit, net: Math.max(0, gross - credit) };
  }

  var tools = {
    mortgage: function () {
      var price = num("price"), downPct = num("down"), rate = num("rate"), years = num("term");
      var mills = num("mills"), ins = num("insurance"), hoa = num("hoa");
      var down = price * downPct / 100, loan = Math.max(0, price - down);
      var pi = pmt(loan, rate, years);
      var tax = ksTax(price, mills).net / 12;
      var insM = ins / 12;
      var pmi = downPct < 20 ? loan * 0.006 / 12 : 0; // illustrative 0.6%/yr
      var total = pi + tax + insM + hoa + pmi;
      set("out-total", usd(total)); set("out-pi", usd(pi)); set("out-tax", usd(tax)); set("out-ins", usd(insM));
      set("out-hoa", usd(hoa)); set("out-pmi", usd(pmi)); set("out-loan", usd(loan)); set("out-down", usd(down));
      set("out-interest", usd(pi * years * 12 - loan));
      bar($("#bar"), [[pi, "#4ade80"], [tax, "#f2c66d"], [insM, "#7aa2ff"], [hoa + pmi, "#f08a5d"]]);
    },
    tax: function () {
      var value = num("value"), mills = num("mills");
      var t = ksTax(value, mills);
      set("out-net", usd(t.net)); set("out-monthly", usd(t.net / 12)); set("out-assessed", usd(t.assessed));
      set("out-gross", usd(t.gross)); set("out-credit", "−" + usd(t.credit, 2)); set("out-rate", (t.net / (value || 1) * 100).toFixed(2) + "%");
      var city = num("citymills"); set("out-city", usd(value * 0.115 * city / 1000));
    },
    afford: function () {
      var inc = num("income"), debts = num("debts"), rate = num("rate"), years = num("term"), downAmt = num("downamt"), mills = num("mills"), ins = num("insurance");
      var mo = inc / 12;
      var front = mo * 0.28, back = mo * 0.36 - debts;
      var budget = Math.max(0, Math.min(front, back));
      // solve price: P&I(price-down) + tax(price)/12 + ins/12 <= budget  (iterate)
      var lo = 0, hi = 5e6;
      for (var i = 0; i < 60; i++) {
        var mid = (lo + hi) / 2;
        var cost = pmt(Math.max(0, mid - downAmt), rate, years) + ksTax(mid, mills).net / 12 + ins / 12;
        if (cost > budget) hi = mid; else lo = mid;
      }
      set("out-price", usd(lo)); set("out-budget", usd(budget)); set("out-front", usd(front)); set("out-back", usd(Math.max(0, back)));
      set("out-loan", usd(Math.max(0, lo - downAmt)));
      var stretch = 0, lo2 = 0, hi2 = 5e6, b2 = Math.max(0, Math.min(mo * 0.33, mo * 0.43 - debts));
      for (var j = 0; j < 60; j++) { var m2 = (lo2 + hi2) / 2; var c2 = pmt(Math.max(0, m2 - downAmt), rate, years) + ksTax(m2, mills).net / 12 + ins / 12; if (c2 > b2) hi2 = m2; else lo2 = m2; }
      stretch = lo2; set("out-stretch", usd(stretch));
    },
    rentbuy: function () {
      var rent = num("rent"), rentGrowth = num("rentgrowth") / 100, price = num("price"), downPct = num("down") / 100, rate = num("rate"),
        mills = num("mills"), appr = num("appr") / 100, years = Math.max(1, Math.round(num("years"))), invest = num("invest") / 100, maint = num("maint") / 100, ins = num("insurance");
      var down = price * downPct, loan = price - down, pi = pmt(loan, rate, 30), r = rate / 100 / 12;
      var closingBuy = price * 0.03, sellCost = 0.07;
      var rentTotal = 0, buyTotal = closingBuy, bal = loan, value = price, curRent = rent;
      var invested = down + closingBuy; // renter invests what buyer spent up front
      var breakeven = null;
      for (var y = 1; y <= years; y++) {
        var buyYear = 0, interestYear = 0;
        for (var m = 0; m < 12; m++) { var int = bal * r; interestYear += int; bal -= (pi - int); }
        buyYear = pi * 12 + ksTax(value, mills).net + ins + value * maint;
        buyTotal += buyYear;
        rentTotal += curRent * 12;
        var diff = buyYear - curRent * 12; // renter invests monthly savings
        invested = invested * (1 + invest) + Math.max(0, diff);
        value *= (1 + appr); curRent *= (1 + rentGrowth);
        var buyerWealth = value * (1 - sellCost) - Math.max(0, bal);
        var renterWealth = invested;
        if (breakeven === null && buyerWealth > renterWealth) breakeven = y;
        if (y === years) {
          set("out-buyer", usd(buyerWealth)); set("out-renter", usd(renterWealth));
          var win = buyerWealth > renterWealth;
          set("out-verdict", win ? "Buying wins" : "Renting wins");
          set("out-gap", usd(Math.abs(buyerWealth - renterWealth)));
        }
      }
      set("out-pi", usd(pi)); set("out-rentpaid", usd(rentTotal)); set("out-buypaid", usd(buyTotal));
      set("out-breakeven", breakeven ? breakeven + " yr" + (breakeven > 1 ? "s" : "") : "Not within " + years + " yrs");
    },
    moving: function () {
      var miles = num("miles"), size = $("#size").value, mode = $("#mode").value, extras = $$("[name=extra]:checked").map(function (e) { return +e.value; });
      var weight = { studio: 2000, "1br": 3500, "2br": 6000, "3br": 9000, "4br": 12000 }[size] || 6000;
      var low, high;
      if (mode === "diy") { low = 120 + miles * 0.9 + weight * 0.01; high = low * 1.6; }
      else if (mode === "container") { low = 900 + miles * 1.1 + weight * 0.05; high = low * 1.5; }
      else {
        if (miles < 100) { var hrs = weight / 1100 + 2; low = hrs * 140; high = hrs * 220; }
        else { low = weight * (0.45 + miles / 4000); high = low * 1.55; }
      }
      var add = extras.reduce(function (a, b) { return a + b; }, 0);
      low += add; high += add * 1.3;
      set("out-low", usd(low)); set("out-high", usd(high)); set("out-mid", usd((low + high) / 2)); set("out-weight", weight.toLocaleString() + " lbs (est.)");
    },
    col: function () {
      var salary = num("salary"), from = num("fromindex"), to = num("toindex");
      var eq = salary * (to / (from || 100));
      set("out-eq", usd(eq)); set("out-diff", (eq >= salary ? "+" : "−") + usd(Math.abs(eq - salary)));
      set("out-pct", ((to / (from || 100) - 1) * 100).toFixed(1) + "%");
    }
  };
  if (tools[tool]) bind(tools[tool]);
})();
