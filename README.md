# Multi-LLM Orchestration Platform

![status](https://img.shields.io/badge/status-prototype-orange) ![license](https://img.shields.io/badge/license-MIT-green) ![built_with](https://img.shields.io/badge/built_with-React-61DAFB) ![styling](https://img.shields.io/badge/styling-Tailwind_CSS-38B2AC)

![Dashboard screenshot](https://github.com/user-attachments/assets/ce54e461-ec7d-4545-a453-8d0e7ff437c0)

*Screenshot of the demo. All figures shown are sample data.*

A front-end prototype that explores how an organization could route requests across several AI model providers instead of depending on one.

**Status: prototype with sample data.** The dashboard does not call any AI provider. The provider status, costs, savings, and market share figures on screen are sample values typed into the source code.

Live demo: https://eaglepython.github.io/multi-llm-orchestration-platform

## The idea

When one vendor supplies the AI behind a critical service, the service inherits that vendor's outages, price changes, and failure modes. A routing layer that can choose among providers by cost, speed, and reliability, and fail over when one is down, reduces that dependence. This prototype shows what the controls and reporting for such a layer could look like.

## What is in the repo

**`src/` (React front end).** A dashboard with five tabs: Overview, Analytics, Cost Optimization, an oversight view of market concentration, and Settings. All numbers are illustrative.

**`Backend/` (design draft, not runnable yet).** A draft of a FastAPI service with a routing engine, a circuit breaker, and unit tests. The files were pasted in from a document and lost their formatting, so they do not run as committed. The design is:

- Score each available provider on cost, latency, and reliability
- Pick a provider by strategy: balanced, cheapest, fastest, or round robin
- Skip a provider after three consecutive failures and retry it after a timeout
- Fall back to the next provider when a call fails

In the draft, one provider is a real API integration and the others are simulated. The front end is not connected to the backend.

## What I would build next

- Restore the backend so it runs and its tests pass
- Connect the dashboard to the backend's metrics endpoint
- Replace simulated providers with real ones and measure actual cost and latency

## Run the front end locally

```bash
git clone https://github.com/eaglepython/multi-llm-orchestration-platform.git
cd multi-llm-orchestration-platform
npm install
npm start
```

## Author

Joseph Bidias

## License

MIT
