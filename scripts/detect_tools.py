#!/usr/bin/env python3
"""Report which creative tools this machine has, and which to use for each creative job.

usage: python3 detect_tools.py [--json]

Checks for command-line tools, installed agent skills and API key NAMES in the environment.
It never prints a key's value, makes no network calls and changes nothing.
"""
import json
import os
import shutil
import sys

HOME = os.path.expanduser("~")
SKILL_DIRS = [os.path.join(HOME, ".claude", "skills"), os.path.join(HOME, ".agents", "skills"), os.path.join(os.getcwd(), ".claude", "skills")]


def skills(prefixes):
    found = set()
    for d in SKILL_DIRS:
        if os.path.isdir(d):
            for n in os.listdir(d):
                if any(n.lower().startswith(p) for p in prefixes):
                    found.add(n)
    return sorted(found)


def have_env(*names):
    return [n for n in names if os.environ.get(n)]


def pil():
    try:
        import PIL  # noqa: F401
        return True
    except Exception:
        return False


def detect():
    t = {
        "higgsfield": {"cli": bool(shutil.which("higgsfield")), "skills": skills(["higgsfield"]),
                       "env": have_env("HIGGSFIELD_API_KEY", "HF_API_KEY")},
        "openai_images": {"cli": bool(shutil.which("codex")), "env": have_env("OPENAI_API_KEY")},
        "google_images": {"cli": bool(shutil.which("gemini")), "env": have_env("GEMINI_API_KEY", "GOOGLE_API_KEY")},
        "hosted_models": {"env": have_env("FAL_KEY", "REPLICATE_API_TOKEN")},
        "local_compose": {"pil": pil(), "ffmpeg": bool(shutil.which("ffmpeg")), "imagemagick": bool(shutil.which("magick") or shutil.which("convert"))},
        "browser": {"skills": skills(["browse", "gstack", "playwright"]), "chrome": bool(shutil.which("google-chrome") or shutil.which("chromium") or os.path.exists("/Applications/Google Chrome.app"))},
    }
    for k, v in t.items():
        v["available"] = any(bool(x) for x in v.values())
    return t


def routes(t):
    hig, oai, goo, host, loc, br = (t[k]["available"] for k in ("higgsfield", "openai_images", "google_images", "hosted_models", "local_compose", "browser"))
    ref_model = [n for n, ok in (("OpenAI image model (edit with the product photo as reference)", oai), ("Google image model (edit with the product photo as reference)", goo), ("Higgsfield image model with the product photo as reference", hig), ("hosted image model that accepts a reference image", host)) if ok]
    typeset = [n for n, ok in (("HTML page + browser screenshot", br), ("Pillow / ImageMagick over the real photo", loc)) if ok]
    video = [n for n, ok in (("Higgsfield image-to-video from an approved still", hig), ("hosted image-to-video model", host), ("ffmpeg push-in / slideshow from approved stills", t["local_compose"]["ffmpeg"])) if ok]
    scene = [n for n, ok in (("Higgsfield product photoshoot", hig),) if ok] + ref_model
    none = ["nothing found: ask the owner for photos, or set up one of the tools in references/creative.md"]
    return {
        "offer_card_exact_price": typeset + ref_model or none,
        "product_in_scene": scene or typeset or none,
        "review_or_text_first_card": typeset or ref_model or none,
        "short_video": video or none,
        "resize_feed_and_story": typeset + ref_model or none,
    }


def main():
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__)
        return
    t = detect()
    r = routes(t)
    if "--json" in sys.argv:
        print(json.dumps({"tools": t, "routes": r}, indent=1))
        return
    print("Creative tools found")
    for k, v in t.items():
        short = lambda x: x if not isinstance(x, list) or len(x) <= 4 else "%s and %d more" % (", ".join(x[:3]), len(x) - 3)
        detail = ", ".join("%s=%s" % (a, short(b)) for a, b in v.items() if a != "available" and b)
        print("  %-14s %s  %s" % (k, "yes" if v["available"] else "no ", detail))
    print("\nUse, in this order (first is preferred)")
    for job, opts in r.items():
        print("  %s" % job)
        for i, o in enumerate(opts, 1):
            print("     %d. %s" % (i, o))


if __name__ == "__main__":
    main()
