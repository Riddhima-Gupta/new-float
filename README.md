# FloatChat AI

FloatChat AI is a single-file Streamlit chat app for exploring bundled Argo float data with Groq-powered responses and Plotly charts.

## Project structure

- `app.py`: Streamlit UI
- `run_app.py`: Reusable backend functions called directly by Streamlit
- `data/my_combinedfinal.csv`: Bundled float dataset
- `requirements.txt`: Minimal deployment dependencies

## Local run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Add your key in `.streamlit/secrets.toml`:
   ```toml
   GROQ_API_KEY = "your_groq_api_key_here"
   ```
3. Start the app:
   ```bash
   streamlit run app.py
   ```

## Streamlit Cloud deployment

1. Push this repository to GitHub.
2. Create a new Streamlit Cloud app pointed at `app.py`.
3. Add `GROQ_API_KEY` in the Streamlit Cloud Secrets UI.
4. Deploy.

## Notes

- There is no Flask, FastAPI, uvicorn, Ollama, ChromaDB, or secondary port.
- If the Groq API is unavailable, the app falls back to a local scientific summary so the UI still stays responsive.
