# ICICI Prudential Mutual Fund RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot that answers questions about ICICI Prudential mutual funds using data from [Groww](https://groww.in/mutual-funds/amc/icici-prudential-mutual-funds) and GROQ LLM.

## Local Setup

1. Copy `.env.example` to `.env` and add your `GROQ_API_KEY`
2. `pip install -r requirements.txt`
3. First run: `python run_local.py --refresh` (scrape + process + index)
4. Start chat: `python run_local.py`

## Streamlit Cloud Deployment

1. Push this repo to GitHub (already at [github.com/amankmr480-bit/Mutualfunds-RAG](https://github.com/amankmr480-bit/Mutualfunds-RAG))
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **"New app"** → **"Deploy an existing app"**
4. Select: **Repository:** `amankmr480-bit/Mutualfunds-RAG`, **Branch:** `main`, **Main file path:** `phase6_chatbot/app.py`
5. **Advanced settings** → Secrets (TOML):
   ```
   GROQ_API_KEY = "your-groq-api-key-here"
   ```
6. Click **"Deploy"**

## Hugging Face Spaces Deployment (Alternative)

Hugging Face Spaces has native Streamlit support and often works better than Streamlit Cloud:

1. Go to [huggingface.co/spaces](https://huggingface.co/spaces) and create a new Space
2. Select **Streamlit** as SDK, choose **Public**
3. Clone your repo or upload files. Set **App file** to `phase6_chatbot/app.py` (or create a root `app.py` that imports it)
4. Add `GROQ_API_KEY` in Space **Settings → Repository secrets**
5. The app will build and deploy automatically

## Vercel Note

Vercel is designed for serverless/static apps and does not support long-running Streamlit processes. For this Streamlit app, use **Streamlit Cloud** or **Hugging Face Spaces** instead.

## Data Source

- [Groww - ICICI Prudential Mutual Fund](https://groww.in/mutual-funds/amc/icici-prudential-mutual-funds)
- [ICICI Prudential AMC](https://www.icicipruamc.com/home)
