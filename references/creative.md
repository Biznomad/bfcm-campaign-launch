# BFCM creative

## Concepts, not variations

Ad platforms group ads that look and say the same thing. A new headline on the same image is the same ad. A new concept changes the hook, the person, the format or the problem. This is agency practice, not a platform rule; let the account's own results decide.

Pick concepts from the store's data first: the best-selling product, the best past ads by purchases, real reviews. Then fill gaps from this slate.

1. Price offer on the real product photo
2. Ladder: more units, lower price each
3. Subscription or best-value first order (state first price, renewal price, interval)
4. Real customer review with their photo
5. The math: regular price against sale price per unit
6. Founder letter, text first
7. How to use it / what comes in the box
8. Product range carousel
9. Gift angle: who it's for, ships by when (only a date the owner confirms)
10. Founder or customer on camera, phone video
11. Last chance: Cyber Monday, same post with new text where the old copy stays true

Minimum set: 1, 2 and 4. A one-month sale needs new concepts each week.

## Which tool makes which creative

Run `python3 scripts/detect_tools.py`. It lists what is installed and the order to try for each job. The reasoning behind the order:

| Job | Best fit | Why |
|---|---|---|
| Offer card with an exact price | Typeset it: HTML page + screenshot, or Pillow over the real product photo | Prices and terms must be exact. Typeset text is never misspelled |
| Same card, richer look | An image model that edits from a reference image, given the real product photo and the exact copy | Keeps the real packaging; check every word after |
| Product in a scene or on a person | Higgsfield product photoshoot if installed; otherwise an image model with the product photo as reference | Built for product placement |
| Review or founder-letter card | Typeset | It is text; no model needed |
| Short video | Higgsfield image-to-video from an approved still if installed; otherwise ffmpeg push-in or slideshow from approved stills | Animating an approved still keeps the label right |
| Feed and story sizes | Re-render the typeset version, or ask the model to recreate the approved image at the new size changing nothing else | Cropping cuts off text |

If the store has its own skills for any of these tools, use them: they carry that tool's current commands. Model names and commands change; read the tool's help before the first call.

No tool at all: typeset on the store's own photos. That is enough for concepts 1, 2, 3, 4, 5, 6 and 8.

## Rules for every image

- Start from real product photos. Generated packaging drifts: zoom in and check every label for spelling, variant name and size.
- One sample, owner approves, then the set. Approval of a style is not approval to launch.
- Only the exact approved copy. No dates in the image; the deadline goes in the ad text.
- Feed 4:5 and story 9:16. Keep the top 12% and bottom 15% of a story free of text.
- Paid tools cost credits. Make one image, check it, then batch. Tell the owner the rough cost before a batch.
- When a price or deadline changes, fix or remake every image that shows it before anything ships.

## Reviews and claims

Real reviews only, word for word, from the store's review app. No health or medical claims. Customer and review counts need a source the owner can show.
