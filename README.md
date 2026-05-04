# AutoRadar — Frontend

> Score de confiance véhicule pour passionnés et collectionneurs européens.

**Live:** https://autoradar-q4s9.vercel.app

## Overview

AutoRadar aggregates car listings from multiple sources, applies AI-powered scoring, and provides a curated discovery experience for premium and exotic vehicles.

This repository contains the **frontend only** — a single-file PWA running entirely in the browser. The companion scraper lives at Vinci75000/autoradar-scraper.

## Stack

- Vanilla HTML / CSS / JS (single-file SPA)
- Supabase (Postgres + RLS) — backend data
- Vercel — hosting + PWA
- Claude API — AI search & scoring

## Structure

    .
    ├── index.html        # Main app (single-file SPA)
    ├── manifest.json     # PWA manifest
    ├── sw.js             # Service worker (offline support)
    └── icon-*.png        # PWA icons (32 → 512 px)

## Status

- App live, PWA installable on iOS and Android
- Frontend currently uses a hardcoded data array — Supabase live fetch in progress
- Auth, alerts, auction view, and ECR integration on the roadmap

## License

Private.
