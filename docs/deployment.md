# Free Deployment Guide

## Recommended Option: Streamlit Community Cloud

This is the best free host for this project because the app is a Python Streamlit dashboard. Netlify is mainly for static sites and frontend apps, while Streamlit needs a running Python process.

Use this setup:

- Platform: Streamlit Community Cloud
- Repository: `DiellzaPervetica/wfm-planning-agent`
- Branch: `main`
- Main file path: `app.py`
- Python version: `3.12`
- Secrets: none

## Steps

1. Open https://share.streamlit.io/
2. Sign in with GitHub.
3. Click `Create app`.
4. Select `Yup, I have an app`.
5. Fill in:
   - Repository: `DiellzaPervetica/wfm-planning-agent`
   - Branch: `main`
   - Main file path: `app.py`
6. Open `Advanced settings`.
7. Set Python version to `3.12`.
8. Leave secrets empty.
9. Click `Deploy`.

After it finishes, Streamlit gives you a public URL like:

```text
https://your-app-name.streamlit.app
```

Copy that URL into:

- `docs/kaggle_writeup.md`
- Your Kaggle submission
- Your video description, if needed

## Why Not Netlify?

Netlify is excellent for static websites and JavaScript frontends, but this app is not static. It runs a Streamlit server with Python code, CSV processing, Plotly charts, file upload widgets, and download buttons. Streamlit Community Cloud is designed for this exact app type.

## Alternative: Hugging Face Spaces

Hugging Face Spaces also has a free Streamlit option, but it requires a Hugging Face account token for CLI deployment. If you prefer this path, create a free token at https://huggingface.co/settings/tokens, then log in locally:

```powershell
huggingface-cli login
```

After login, the project can be uploaded as a Streamlit Space.
