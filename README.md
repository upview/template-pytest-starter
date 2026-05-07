# Pytest Starter

Pure pytest procedure for TofuPilot — zero imports from us.

Each test function is a phase. Outcome (PASS/FAIL/SKIP/XFAIL) comes from pytest itself. Recognized assert shapes also become measurements on the dashboard, with description and unit pulled from `"Description [unit]"` assertion messages.

For prompts, attachments, multi-dim charts, marginal limits, or measurement-rich procedures: use the OpenHTF connector or the TofuPilot Framework.

## Run locally

```
uv run pytest
```

## Deploy via TofuPilot

1. Sign up at [tofupilot.app](https://www.tofupilot.app/auth/signup).
2. Open **New Procedure** in the dashboard and clone this template (or import this repo).
3. Push to GitHub — TofuPilot deploys to your stations automatically.
