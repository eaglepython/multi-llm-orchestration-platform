<div align="center">

# Multi-LLM Orchestration Platform

### A dashboard concept for routing requests across several AI providers to reduce single-vendor dependence.

![Status](https://img.shields.io/badge/Status-Prototype-E67E22?style=flat-square)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=white)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI_(draft)-009688?style=flat-square&logo=fastapi&logoColor=white)
![Tailwind](https://img.shields.io/badge/Styling-Tailwind_CSS-38B2AC?style=flat-square&logo=tailwindcss&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-2E7D32?style=flat-square)

[**Live demo →**](https://eaglepython.github.io/multi-llm-orchestration-platform/)

<br/>

<img src="https://github.com/user-attachments/assets/ce54e461-ec7d-4545-a453-8d0e7ff437c0" alt="Dashboard" width="90%"/>

</div>

---

> [!NOTE]
> **Status: prototype with sample data.** The dashboard does not call any AI provider — the status, cost, savings, and market-share figures on screen are sample values. The backend is a design draft (see below).

## The idea

When one vendor supplies the AI behind a critical service, the service inherits that vendor's outages, price changes, and failure modes. A routing layer that can pick among providers by cost, speed, and reliability — and fail over when one is down — reduces that dependence. This project sketches the controls and reporting for such a layer.

## What's in the repo

### `src/` — React front end
A dashboard with five tabs: Overview, Analytics, Cost Optimization, a market-concentration view, and Settings. All numbers are illustrative.

### `Backend/` — design draft (not runnable yet)
A FastAPI service with a routing engine, a circuit breaker, and unit tests. The files were pasted from a document and lost their formatting, so they do not run as committed. The intended design:

- Score each available provider on cost, latency, and reliability
- Select by strategy — balanced, cheapest, fastest, or round-robin
- Trip a circuit breaker after repeated failures and retry after a timeout
- Fall back to the next provider when a call fails

## Run the front end locally

```bash
git clone https://github.com/eaglepython/multi-llm-orchestration-platform.git
cd multi-llm-orchestration-platform
npm install
npm start
```

## Roadmap

- Restore the backend so it runs and its tests pass
- Connect the dashboard to the backend's metrics endpoint
- Swap simulated providers for real ones and measure actual cost and latency

## Author

**Joseph Bidias** — [github.com/eaglepython](https://github.com/eaglepython)

<sub>Released under the MIT License.</sub>
