# Melanie Li Research

Weekly-updated research dashboard tracking the Cantonese American creator
landscape for Melanie Li ([@melanie_li](https://www.instagram.com/melanie_li)):
similar creators, viral video formats, tailored content ideas, and a weekly
trend watch.

## Live dashboard

Deployed on Vercel from this repo (auto-deploys on every push to `main`).

## How the weekly update works

1. A scheduled job runs `python3 build.py`, which refreshes follower counts
   for Melanie and every creator on the watchlist via the connected
   Instagram account and stamps `data.json` with a new `updated_at`.
2. The job then runs a social listening pass (Instagram/Facebook/Threads)
   for new viral Cantonese-creator content and **prepends** a dated entry to
   the `trends` array in `data.json` — never rewriting history, never
   inventing rows.
3. Changes are committed and pushed to `main`; Vercel redeploys automatically.

## Local preview

```sh
python3 -m http.server 8000
# open http://localhost:8000
```
