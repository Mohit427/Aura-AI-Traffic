# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project context

This is the React frontend for **AURA**, an AI traffic-signal control system built for a hackathon (SIH 2026). It's one of several layers in the parent project (`../backend`, `../engine`, `../sumo_simulation`, `../vision`) — see `../CONTRACTS.md` for the full JSON schema contracts shared across layers (Vision, TomTom, Digital Twin, Engine, EV Conflict, Advisor). This frontend is a **read-mostly dashboard**: it polls the backend for the live engine decision and renders it, plus one write path to an LLM-backed "advisor" endpoint for a plain-English explanation.

Demo intersection: Vadapalani Junction, Chennai.

## Commands

- `npm run dev` — start the Vite dev server
- `npm run build` — production build
- `npm run preview` — preview the production build
- `npm run lint` — run ESLint (flat config in `eslint.config.js`; no test runner is configured in this project)

## Architecture

**Data flow:** `App.jsx` is the single source of truth for state. It polls `GET /api/latest-decision` every 2 seconds (`src/api.js`) and passes the resulting `engineData` object down to presentational components as props. No routing, no global state library — just one `useState` + `useEffect` poll loop at the top.

- `engineData` shape matches the **Engine Output** contract in `../CONTRACTS.md` (`phase_durations`, `priority_mode`, `vui_score`), extended with an `ev_schedule` field (from the backend's `ev_schedule` persistence) when `priority_mode === 'emergency_vehicle'`.
- `App.jsx`'s `buildEvData()` derives the `ev_data`/`ev_stage`/`downstream_green_wave` fields consumed by `EVConflictPanel` from the raw `ev_schedule` — this is real backend data, not fabricated placeholder data (see recent commit "remove frontend EV data fabrication"). Do not reintroduce hardcoded/fake EV fields here.
- Components are dumb/presentational and keyed off `priorityMode`/`priority_mode`:
  - `VUIGauge` — SVG radial gauge, animates when `priorityMode === 'vulnerable_user'`.
  - `SignalTimeline` — proportional bar chart of `phase_durations`.
  - `EVConflictPanel` — renders `null` unless `priority_mode === 'emergency_vehicle'` and `ev_data` is present; shows the 3-stage EV preemption tracker.
  - `AdvisorPanel` — the one component with its own side effect: on every `engineData` change it independently `POST`s to `/api/advisor/explain` with `{ engine_output: engineData }` and renders the returned natural-language `explanation`.
- Each component pairs 1:1 with its own CSS file (e.g. `VUIGauge.jsx` + `VUIGauge.css`) — no CSS-in-JS, no shared component library.

**Backend calls:** Both `src/api.js` and `AdvisorPanel.jsx` hardcode the same production API base URL (`https://aura-backend-v27b.onrender.com`) and send `Authorization: Bearer ${import.meta.env.VITE_CORA_TOKEN}` on every request. `VITE_CORA_TOKEN` must be set in the environment (e.g. `.env.local`, gitignored via `*.local`) for API calls to succeed locally. If you add a new backend call, follow this same pattern (base URL constant + bearer token header) rather than introducing a new HTTP client or auth scheme — and check `../CONTRACTS.md` first for the expected request/response shape.

## Note on `../backend/CLAUDE.md`

The `CLAUDE.md` inside `../backend/` is not a description of the backend service — it's an unrelated Swytchcode MCP tool-use contract that happens to live in that directory. Don't treat it as backend architecture documentation.
