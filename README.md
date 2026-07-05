# 🚀 Skills

This repository contains **2** reusable agent skills.

## 🛠️ Available Skills & Performance

<div class="overflow-x: auto; width: 100%;" markdown="block">

| Skill | Description | Boosts This Run | Total Boosted (Lifetime) | Est. Weekly Boost | Installation |
|:------|:------------|:----------------|:-------------------------|:------------------|:-------------|
| `badge-maker` | Use this skill whenever the user wants to create pill-shaped icon+label badges — language selector badges, status badges (Live/Beta/New), tag chips, category labels, or similar small rounded UI badges with an icon square on the left and a text label on the right. Trigger this for requests like "make a badge for X", "create language badges", "design a status pill", "make tag chips for my site", or any request to recreate/extend badges shown in an uploaded screenshot. Always use this skill's interview flow (ask about badge content, colors, and layout) rather than guessing at colors or shapes — it produces transparent PNGs via a tested font pipeline that downloads the exact font needed for whatever text the user wants (Devanagari, Bengali, Arabic, Tamil, Thai, Hebrew, CJK, and more) and renders it with correct shaping, which a generic approach will get wrong. | 100 | 1400 | ~700 | `npx skills add besaoct/skills --skill badge-maker` |
| `flutter-app-with-react-admin-architecture` | Reference architecture for bootstrapping new Flutter mobile apps and React/Vite/Tailwind web admin panels, based on a proven cross-platform codebase. Use whenever the user is starting a new Flutter or React admin project, asking how to structure a Flutter app (layered architecture, Riverpod, GoRouter, Drift), wants a custom animated tab bar, needs Firebase Crashlytics on Android/iOS, is setting up Tailwind CSS v4 with Vite, needs responsive layout down to 320px, wants theme/design-token conventions, or needs blueprints for in-app updates version check, RevenueCat dynamic MRR analytics, broadcasts/announcements, admin whitelisting, version sync automation, Fastlane pipelines, and Firestore security rules. Trigger even without the words "architecture" or "template" — e.g. "how should I structure my Flutter app", "build me a liquid tab bar", "set up Tailwind v4 with Vite", "add crash reporting to my Flutter app" all qualify. | 100 | 2700 | ~700 | `npx skills add besaoct/skills --skill flutter-app-with-react-admin-architecture` |

</div>

## 📊 Stats Overview
- **Last Updated:** 2026-07-05 04:17 UTC
- **Frequency:** Every 24 Hours
- **Total Runs:** 18
- **Total Successful Boosts:** 4100
- **Average Boosts Per Run:** 227
- **Estimated Weekly Boost:** ~1400
