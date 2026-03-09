# ICICI Prudential Mutual Fund RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot that answers questions about ICICI Prudential mutual funds using data from [Groww](https://groww.in/mutual-funds/amc/icici-prudential-mutual-funds) and GROQ LLM.

## Local Setup

1. Copy `.env.example` to `.env` and add your `GROQ_API_KEY`
2. `pip install -r requirements.txt`
3. First run: `python run_local.py --refresh` (scrape + process + index)
4. Start chat: `python run_local.py`

## Streamlit Cloud Deployment

1. Fork/push this repo to your GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo and set **Main file path** to `phase6_chatbot/app.py`
4. Add secret `GROQ_API_KEY` in Streamlit Cloud dashboard (Settings → Secrets)
5. Deploy

## Data Source

- [Groww - ICICI Prudential Mutual Fund](https://groww.in/mutual-funds/amc/icici-prudential-mutual-funds)
- [ICICI Prudential AMC](https://www.icicipruamc.com/home)
