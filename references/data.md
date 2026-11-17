# Use the store's own numbers

Pull these before setting any price or budget. Read-only. Say which ones you could not get; do not fill gaps with guesses or industry averages presented as the store's.

## What to pull

| Source | Pull | It decides |
|---|---|---|
| Store orders, last year's BFCM week (if the store existed) | orders, sales, average order, new vs returning customers, top products, discount depth, sales by day and hour | this year's target, hero product, how deep to discount, when to send |
| Store orders, last 90 days | best sellers by units and by sales, average order, repeat rate, share of subscription orders | which products lead, bundle sizes, whether to push subscription |
| Product costs | unit cost per product, shipping and packing cost per order, payment fees | what each offer leaves, the cap per new customer (`plan.py`) |
| Inventory | units on hand and on order for each sale product | which offers are safe to promote, when to stop an ad |
| Site analytics, last 30 days | sessions, add-to-cart rate, checkout rate, by device, landing page and traffic source | where to send ad traffic, what to fix before the sale |
| Ad accounts, last 30 and 90 days | spend, purchases, cost per purchase by campaign and by ad; best posts by purchases | budget, which concepts to reuse, which posts to keep for their likes |
| Email and text platform | list sizes, engaged segment sizes, sales per send, best send times, which flows are on | audience order, send times, how many sends the list tolerates |
| Reviews app | real review text and photos, count and rating | review creatives and claims you can back up |
| Shipping settings | free-shipping threshold, rates | whether each sale price crosses the threshold |

## Turning numbers into offers

1. **Hero offer** = the best seller with healthy stock and margin. Not the product the owner likes most.
2. **Ladder.** Two or three steps where the price per unit falls and one step crosses the free-shipping threshold. Check every step in `plan.py`: an offer that leaves nothing before ads is rejected.
3. **Depth.** Start from last year's depth and what it left per order. Deeper only if the cap per new customer still clears the store's real cost per purchase from the ad account.
4. **Subscription or bundle first** when repeat rate is high: a first order that breaks even can pay back on the second.
5. **Budget.** Ad budget = planned new customers x cap, or the owner's number if lower. `plan.py` splits it by phase; move it toward what beats the cap.
6. **Target.** Last year's BFCM sales, adjusted by how this year's last 90 days compare with the same 90 days a year ago. State it as a range and name the assumption.

## No history

New store or no access: use the last 90 days only, a shallower discount, a smaller budget for the first two days, and say so on the plan.
