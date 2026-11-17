#!/usr/bin/env python3
"""Plan a Black Friday / Cyber Monday campaign from today through Cyber Monday.

usage: python3 plan.py bfcm.config.json [--today YYYY-MM-DD] [--json]

Works out this year's Black Friday and Cyber Monday, the sale window for the chosen
sale_length (1w, 2w or 1m, always ending Cyber Monday), the phases between today and
the sale, unit economics, an ad budget split and a day-by-day calendar.
Makes no network calls and changes nothing.
"""
import datetime
import json
import sys

SALE_DAYS = {"1w": 7, "2w": 14, "1m": 30}
# Starting split of the total ad budget. Adjust with the store's own numbers.
PRE_SALE_SHARE = {"warmup": 0.15, "teaser": 0.10}  # share of the total, whatever the phase length
DAY_WEIGHT = {"sale": 3, "peak": 6, "cyber": 7}  # relative spend per day once the sale is open
D = datetime.timedelta


def black_friday(year):
    d = datetime.date(year, 11, 1)
    first_thu = d + D(days=(3 - d.weekday()) % 7)
    return first_thu + D(days=22)  # day after the fourth Thursday


def margin(price, units, c):
    fees = price * c.get("payment_fee_pct", 2.9) / 100 + c.get("payment_fee_fixed", 0.30)
    return round(price - units * c["unit_cost"] - c["shipping_cost_per_order"] - fees, 2)


def economics(c):
    rows = []
    for o in c["offers"]:
        m = margin(o["bfcm_price"], o["units"], c)
        off = round(100 * (1 - o["bfcm_price"] / o["regular_price"])) if o.get("regular_price") else None
        rows.append({"offer": o["name"], "price": o["bfcm_price"], "percent_off": off, "left_per_order": m,
                     "max_cost_per_new_customer": m if m > 0 else 0,
                     "break_even_return": round(o["bfcm_price"] / m, 2) if m > 0 else None})
    s = c.get("subscription")
    if s:
        first = margin(s["first_order_price"], s["units"], c)
        renew = margin(s["renewal_price"], s["units"], c)
        n = max(1, int(c.get("target_payback_orders", 2)))
        rows.append({"offer": "Subscription", "price": s["first_order_price"], "percent_off": None,
                     "left_per_order": first, "left_per_renewal": renew,
                     "max_cost_per_new_customer": round(first + renew * (n - 1), 2),
                     "break_even_return": None, "payback_orders": n})
    return rows


def windows(c, today):
    year = c.get("year") or today.year
    bf = black_friday(year)
    cm = bf + D(days=3)
    if not c.get("year") and today > cm:
        bf = black_friday(year + 1)
        cm = bf + D(days=3)
    opens = cm - D(days=SALE_DAYS[c["sale_length"]] - 1)
    late = False
    if today >= opens:  # installed after the planned opening: open as soon as a short build allows
        late = True
        opens = min(today + D(days=2), cm)
    runway = (opens - today).days
    build_days = min(7, runway)  # 0 when the skill is installed on Cyber Monday itself
    teaser_days = max(0, min(7, runway - build_days))
    build_end = today + D(days=build_days - 1)
    teaser_start = opens - D(days=teaser_days)
    w = {"today": today, "black_friday": bf, "cyber_monday": cm, "sale_opens": opens, "late_start": late,
         "runway_days": runway, "phases": []}

    def add(name, a, b):
        if a <= b:
            w["phases"].append({"phase": name, "start": a, "end": b, "days": (b - a).days + 1})

    if runway > 0:
        add("build", today, min(build_end, opens - D(days=1)))
    add("warmup", build_end + D(days=1), teaser_start - D(days=1))
    add("teaser", max(teaser_start, build_end + D(days=1)), opens - D(days=1))
    thanksgiving = bf - D(days=1)
    add("sale", opens, min(thanksgiving - D(days=1), cm))
    add("peak", max(opens, thanksgiving), bf + D(days=2))
    add("cyber", max(opens, cm), cm)
    add("close", cm + D(days=1), cm + D(days=7))
    return w


def phase_of(w, d):
    for p in w["phases"]:
        if p["start"] <= d <= p["end"]:
            return p
    return None


def calendar(c, w):
    ch = c["channels"]
    ads = ch.get("meta_ads") or ch.get("google_ads")
    plan = []
    d = w["today"]
    end = w["cyber_monday"] + D(days=7)
    bf, cm, opens = w["black_friday"], w["cyber_monday"], w["sale_opens"]
    while d <= end:
        p = phase_of(w, d)
        name = p["phase"] if p else ""
        i = (d - p["start"]).days if p else 0
        last = p and d == p["end"]
        t = []
        if name == "build":
            steps = ["Audit every channel; pull last year's BFCM and the last 90 days (references/data.md)",
                     "Lock offers and caps from the data; run scripts/detect_tools.py; make ONE sample creative for approval",
                     "Create discounts (scheduled); build the preview theme; set up the early-access signup",
                     "Build the creative set; stage ads paused; draft every email, text and push",
                     "Phone walk of the preview theme; test the cart; fix what breaks",
                     "Review page to the owner: every asset, link, price and date",
                     "Buffer: fixes from the owner's review"]
            n = p["days"]
            # squeeze the seven build steps into however many build days exist
            lo, hi = i * len(steps) // n, (i + 1) * len(steps) // n
            t += steps[lo:max(hi, lo + 1)]
        elif name == "warmup":
            if i == 0:
                t.append("Start list building: early-access signup live on site, in bio and in flows")
                if ads:
                    t.append("Concept test at low budget on the evergreen offer: find 2-3 winning concepts before the sale")
            if i % 7 == 3 and ch.get("email"):
                t.append("Email: value or story, no sale price; invite to the early-access list")
            if i % 7 == 6:
                t.append("Review: list growth, cost per signup, which concepts get the cheapest purchases")
            if ch.get("organic_social") and i % 2 == 0:
                t.append("Organic post (approved slots only)")
        elif name == "teaser":
            if i == 0:
                t.append("Teaser goes up: sale date announced, no prices unless the owner says so")
                if ch.get("email"):
                    t.append("Email: mark your calendar + join early access")
            if last:
                if ch.get("email"):
                    t.append("Email to early-access list: opens tomorrow, what the offers are")
                if ch.get("sms"):
                    t.append("Text to early-access list: opens tomorrow")
                t.append("Final check: discounts scheduled for the right hour, ads paused and approved, theme ready, inventory counted")
            if ch.get("organic_social") and i % 2 == 0:
                t.append("Organic post: countdown (approved slots only)")
        elif name in ("sale", "peak", "cyber"):
            if d == opens:
                if w["runway_days"] == 0:
                    t.append("Same-day build: discounts, three core creatives, one email and one text. Owner approves each before it goes")
                t.append("LAUNCH on the owner's word: publish theme, confirm discounts in a real cart, flip ads")
                if ch.get("email"):
                    t.append("Email: sale is open (early-access list first, full list a few hours later)")
                if ch.get("sms"):
                    t.append("Text: sale is open")
            if name == "sale" and d != opens:
                if ch.get("email") and i % 3 == 0:
                    t.append("Email: new angle (best seller, bundle math, reviews)")
                if ads and i % 7 == 6:
                    t.append("Creative refresh: add new concepts, pause ads over the cost cap")
            if d == bf - D(days=1) and d != opens:
                t.append("Thanksgiving: light touch. One email at most; raise budgets tonight for tomorrow")
            if d == bf:
                if ch.get("email"):
                    t.append("Email: Black Friday (morning) + resend to non-openers (evening)")
                if ch.get("sms"):
                    t.append("Text: Black Friday")
                if ads:
                    t.append("Ads: peak budget; check spend and cost per new customer at midday and evening")
            if d in (bf + D(days=1), bf + D(days=2)):
                if ch.get("email"):
                    t.append("Email: weekend (best sellers going, what's left)")
            if d == cm:
                if ch.get("email"):
                    t.append("Email: Cyber Monday morning + 'ends tonight' in the evening")
                if ch.get("sms"):
                    t.append("Text: ends tonight")
                t.append("Close at %s: discounts end, ads stop, theme restored" % c.get("end_time_local", "23:59"))
            if ch.get("app_push") and (d in (opens, bf, cm)):
                t.append("App push")
            if ch.get("organic_social"):
                t.append("Organic post (approved slots only)")
            if d != opens:
                t.append("Daily check: sales, spend, new customers, cost per new customer vs cap, stock")
        elif name == "close":
            if i == 0:
                t.append("Confirm in a real cart that discounts ended; confirm ads stopped; theme back to normal")
            if i == 1 and ch.get("email"):
                t.append("Email: thank you + what to expect (shipping times). No new discount")
            if last:
                t.append("Results report: sales, spend, new customers, cost per new customer vs cap, best concepts, what to repeat next year")
        if d == bf:
            t.insert(0, "** BLACK FRIDAY **")
        if d == cm:
            t.insert(0, "** CYBER MONDAY **")
        plan.append({"date": d.isoformat(), "day": d.strftime("%a"), "phase": name, "tasks": t})
        d += D(days=1)
    return plan


def budget(c, w):
    total = c.get("ad_budget_total")
    if not total:
        return []
    ph = {p["phase"]: p for p in w["phases"]}
    out, left = [], float(total)
    for name in ("warmup", "teaser"):  # fixed, capped shares before the sale
        if name in ph:
            amt = total * PRE_SALE_SHARE[name]
            left -= amt
            out.append((name, amt))
    live = [n for n in ("sale", "peak", "cyber") if n in ph]
    weight = sum(DAY_WEIGHT[n] * ph[n]["days"] for n in live)
    if not live:
        return []
    for n in live:  # the rest goes by day weight, so a peak day always gets more than an ordinary sale day
        out.append((n, left * DAY_WEIGHT[n] * ph[n]["days"] / weight))
    return [{"phase": n, "days": ph[n]["days"], "total": round(a, 2), "per_day": round(a / ph[n]["days"], 2)} for n, a in out]


def iso(o):
    return o.isoformat() if isinstance(o, datetime.date) else str(o)


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0 if len(sys.argv) > 1 else 2)
    c = json.load(open(sys.argv[1]))
    if c.get("sale_length") not in SALE_DAYS:
        sys.exit("sale_length must be one of: 1w, 2w, 1m")
    for k in ("offers", "unit_cost", "shipping_cost_per_order", "channels"):
        if k not in c:
            sys.exit("missing config key: " + k)
    today = datetime.date.today()
    if "--today" in sys.argv:
        today = datetime.date.fromisoformat(sys.argv[sys.argv.index("--today") + 1])
    w = windows(c, today)
    eco, cal, bud = economics(c), calendar(c, w), budget(c, w)
    if "--json" in sys.argv:
        print(json.dumps({"windows": w, "economics": eco, "budget": bud, "calendar": cal}, indent=1, default=iso))
        return
    print("%s: Black Friday / Cyber Monday plan" % c.get("brand", ""))
    print("Today %s | Black Friday %s | Cyber Monday %s" % (w["today"], w["black_friday"], w["cyber_monday"]))
    print("Sale (%s): opens %s, ends Cyber Monday %s | %d days until it opens" % (
        c["sale_length"], w["sale_opens"], c.get("end_time_local", "23:59"), w["runway_days"]))
    if w["late_start"]:
        print("LATE START: the planned opening has passed. The sale opens %s after a short build. Skip nothing in the build list; cut warm-up and teaser." % w["sale_opens"])
    if w["runway_days"] > 120:
        print("More than four months out: do the build and list building now, and run this again in early October for the final offers.")
    print("\nPhases")
    for p in w["phases"]:
        print("  %-7s %s to %s  (%d days)" % (p["phase"], p["start"], p["end"], p["days"]))
    print("\nMoney left per order before ads")
    for r in eco:
        line = "  %-16s price $%.2f" % (r["offer"], r["price"])
        if r.get("percent_off") is not None:
            line += "  (%d%% off)" % r["percent_off"]
        line += "  left $%.2f  max cost per new customer $%.2f" % (r["left_per_order"], r["max_cost_per_new_customer"])
        if r.get("break_even_return"):
            line += "  break-even return %.2fx" % r["break_even_return"]
        if r.get("payback_orders"):
            line += "  (pays back by order %d; each renewal leaves $%.2f)" % (r["payback_orders"], r["left_per_renewal"])
        if r["left_per_order"] <= 0:
            line += "  ** LOSES MONEY BEFORE ADS: change this offer **"
        print(line)
    if bud:
        print("\nAd budget $%s, starting split (move money toward what beats the cap)" % c["ad_budget_total"])
        for b in bud:
            print("  %-7s %2d days  $%.2f total  $%.2f a day" % (b["phase"], b["days"], b["total"], b["per_day"]))
    print("\nCalendar")
    for d in cal:
        if d["tasks"]:
            print("  %s %s  [%s]" % (d["day"], d["date"], d["phase"]))
            for t in d["tasks"]:
                print("     - " + t)


if __name__ == "__main__":
    main()
