# Deployment guide — Render (Streamlit) + Netlify (static iframe)

This repository contains a Streamlit app (`app.py`) backed optionally by Supabase. The following files were added to make deployment easier:

- `Procfile` — start command used by Render and similar PaaS.
- `Dockerfile` — optional container image build for Render (or any container host).
- `.streamlit/config.toml` — recommended Streamlit runtime config for deployed environments.
- `site/index.html` — minimal static site intended for Netlify that embeds the deployed app via an iframe (replace placeholder URL with your Render app URL).

Important security note
- Never expose your Supabase `service_role` key in client-side code or in static sites. Put secrets in Render environment variables (or other secure secret managers).
- Prefer using the anon key for client-side read-only features and enforce Row Level Security (RLS) in Supabase.

Quick Render deploy (recommended)

1. Push this repo to GitHub.
2. Go to https://render.com and create a new **Web Service**.
   - Connect your GitHub repo and choose the branch (e.g. `main`).
   - Build Command: (leave blank or) `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.enableCORS false`
   - Instance type: free or paid depending on needs.
3. Add environment variables in Render's dashboard for the service:
   - `SUPABASE_URL` = your supabase url
   - `SUPABASE_ANON_KEY` = your anon key
   - (Only if strictly required for server admin operations) `SUPABASE_SERVICE_ROLE` — keep this protected and do not expose to the browser.
4. Deploy and watch logs. When ready, Render gives you a public URL (e.g. `https://your-app.onrender.com`).

Netlify static site with iframe (optional)

1. Replace `site/index.html` iframe `src` with the Render app URL.
2. Push the `site` folder to GitHub (in this repo or another).
3. In Netlify, create a new site from Git -> point to the repo and set the publish directory to `site` (or root if you placed index.html in repo root).
4. Deploy. Visit the Netlify URL to confirm the iframe loads. If the iframe is blank:
   - Check browser console/network for `X-Frame-Options` or `Content-Security-Policy` preventing framing.
   - If the Render app sends `X-Frame-Options: DENY` or `SAMEORIGIN`, the iframe will be blocked. Prefer linking directly to the Render app or host both under same domain.

Troubleshooting
- Build fails: add missing packages to `requirements.txt` and redeploy.
- Supabase connection fails: verify env vars in Render and that keys are correct.
- Framing blocked: either configure headers on host (if possible), use a proxy to strip headers (advanced), or link out to the app instead of embedding.

Local testing commands (PowerShell)

Install deps and run locally:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Simulate platform PORT env:

```powershell
$env:PORT = 8080; streamlit run app.py --server.port $env:PORT --server.address 0.0.0.0
```

If you'd like, I can:
- Prepare a small `render.yaml` snippet with recommended values you can paste into Render UI.
- Create a tiny reverse-proxy example (Flask) to strip frame-blocking headers (if you want to force iframe embedding).
