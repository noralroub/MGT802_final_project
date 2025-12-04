# Streamlit Cloud Deployment Guide

## Quick Start - Deploy to Streamlit Cloud

### 1. Prerequisites
- GitHub account with this repo pushed to it
- Streamlit Cloud account (free at https://streamlit.io/cloud)

### 2. Push to GitHub (if not already done)
```bash
git push origin nora-dev2
```

### 3. Deploy to Streamlit Cloud
1. Go to https://share.streamlit.io
2. Click **"New app"**
3. Fill in:
   - **Repository**: `<your-github-user>/MGT802_final_project`
   - **Branch**: `nora-dev2` (or `main`)
   - **Main file path**: `app.py`
4. Click **Deploy!**

Streamlit will automatically:
- Install dependencies from `requirements.txt`
- Run `app.py`
- Provide you with a public URL

### 4. Access Your App
Your app will be available at:
```
https://share.streamlit.io/YOUR_GITHUB_USER/MGT802_final_project/BRANCH_NAME/app.py
```

## Local Testing (Optional)
To test locally before deploying:
```bash
pip install -r requirements.txt
streamlit run app.py
```

The app will start at `http://localhost:8501`

## Troubleshooting
- **ImportError**: Make sure all dependencies are in `requirements.txt`
- **App not loading**: Check logs in Streamlit Cloud dashboard
- **File not found**: Ensure paths are relative to the project root
