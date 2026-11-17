---
name: bfcm-campaign-launch
description: Use when planning, staging or running a Black Friday / Cyber Monday sale for an ecommerce store, starting from today and running through Cyber Monday (1-week, 2-week or 1-month sale), using the store's own analytics to set offers and budgets and the installed image and video tools to make the ad creatives. Triggers on "Black Friday plan", "BFCM", "Cyber Monday", "holiday sale", "plan my Black Friday".
---

# Black Friday / Cyber Monday Campaign Launch

Starts the day it is installed. Plans every day from today to Cyber Monday, sets offers from the store's own numbers, makes the creatives with whatever tools are on the machine, and stages every channel. **Everything is built paused, draft or on a preview theme. The owner's word "launch" flips it.**

## 1. Start today

1. Copy `bfcm.config.example.json` to the project as `bfcm.config.json`. Fill in what the owner already knows: store, products, costs, channels, `sale_length` (`1w`, `2w` or `1m`; the sale always ends Cyber Monday night).
2. Run `python3 scripts/plan.py bfcm.config.json`. It finds this year's dates, counts the days left, splits them into phases (build, warm-up, teaser, sale, peak, Cyber Monday, close) and prints the calendar. With little time left it shortens warm-up and teaser first and says so.
3. Pull the store's data before fixing prices: `references/data.md`. Put the offers the data supports into the config and run the planner again for the caps and budget split.
4. Run `python3 scripts/detect_tools.py` to see which creative tools exist and which to use for each job.
5. Show the owner the plan, the offers with what each order leaves, and one sample creative. Build after they approve.

## 2. Rules that hold on every run

- **Writes:** confirm the account, store and theme before the first change. Stage on an unpublished theme; never write to the live theme. Back up each file before changing it and log every change with a timestamp.
- **Sends:** emails, texts and pushes stay drafts until the owner says to schedule them. Set the send time and read it back before starting the send job; a send job with no saved time sends now.
- **Spend:** ads are created paused. Read billing status and today's spend before any status flip. Never raise a budget without the owner's number.
- **No early promotion:** sale prices appear nowhere (site, ads, emails, posts) before the day the owner approved. Before the sale, check the live site and every scheduled item for sale wording.
- **Credentials** stay in the environment they live in. Never print them, never copy them between clients.
- **Claims:** only the exact offers, prices and terms in the config. No health claims, no invented reviews, no fake countdowns, no "free shipping" a cart at the sale price doesn't get. No exact dates baked into images.
- **Report what happened.** A step that failed or was skipped is stated as such.

## 3. The run, by phase

1. **Build.** Audit every channel for what is live, scheduled or in conflict (old codes that stack, last year's drafts with dead offers, unpaid bills pausing sends or ads). Schedule discounts for the exact hour. Build the preview theme, creatives, paused ads and draft messages. Walk the preview on a phone and read the cart after every tap. Send the owner one review page.
2. **Warm-up** (only when there is time). Grow the early-access list and test concepts at low budget on the regular offer, so the sale starts with proven ads. `references/phases.md`.
3. **Teaser.** Announce the date. Early-access list hears first.
4. **Sale, peak, Cyber Monday.** Launch on the owner's word, verify each flip took effect, then check daily against the caps. `references/ads.md`, `references/messaging.md`.
5. **Close.** Confirm in a real cart that discounts ended, ads stopped and the theme is back. Report results against the caps and write down what to repeat next year.

## 4. Look up the rest

- What to pull from analytics and what each number decides → `references/data.md`
- What each phase is for, and what to cut when time is short → `references/phases.md`
- Concepts for BFCM ads and which tool makes which creative → `references/creative.md`
- Ad account structure and keeping likes on ads → `references/ads.md`
- Email, text and push rules → `references/messaging.md`
- Sales or add-to-cart dropped mid-sale → `references/diagnose.md`
- Platform traps that cost a retry → `references/traps.md`
