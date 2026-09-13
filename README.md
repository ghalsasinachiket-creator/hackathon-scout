# Hackathon Scout

Hackathon Scout is a Streamlit app that searches multiple hackathon sources, merges and deduplicates the results, uses an LLM to explain why each result matches the user's goal, enriches top results with detail-page information, and exports deadlines as a calendar file.

**Live app:** [https://hackathon-scout-kbnyxom3yhuggntbyzr7ys.streamlit.app/](https://hackathon-scout-kbnyxom3yhuggntbyzr7ys.streamlit.app/)

## Features

- Searches Devpost, Devfolio, and Unstop.
- Deduplicates hackathons across sources by title.
- Uses Groq's OpenAI-compatible API to add a `why` justification column.
- Uses Anakin URL Scraper to enrich shortlisted results with detail-page fields such as team size.
- Exports parsed deadlines as a downloadable `.ics` calendar file.
- Supports local `.env` files and Streamlit Cloud secrets.
- Avoids accidental Unstop RapidAPI quota usage unless live fetching is explicitly enabled.

## Project Structure

```text
.
|-- app.py                    # Streamlit UI
|-- agent.py                  # Main orchestration pipeline
|-- reasoning.py              # Groq-powered relevance reasoning
|-- anakin_enrich.py          # Anakin URL Scraper enrichment
|-- calendar_export.py        # .ics calendar generation
|-- config.py                 # Env var / Streamlit secrets helper
|-- schema.py                 # Shared result shape
|-- clients/
|   |-- devpost_client.py     # Devpost API client
|   |-- devfolio_client.py    # Devfolio GraphQL client
|   `-- unstop_client.py      # Unstop RapidAPI client with cache protection
`-- requirements.txt
```

## Requirements

- Python 3.11+
- Groq API key for reasoning
- Anakin API key for page enrichment
- RapidAPI key for Unstop, if using Unstop live fetches

Devpost and Devfolio do not require API keys in the current implementation.

## Local Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `clients/.env`:

```env
GROQ_API_KEY=your_groq_api_key
ANAKIN_API_KEY=your_anakin_api_key
RAPIDAPI_KEY=your_rapidapi_key
```

Run the Streamlit app:

```bash
streamlit run app.py
```

## Streamlit Cloud Secrets

Streamlit Cloud does not read your local `.env` file. Add the same keys in Streamlit Cloud under **Manage app -> Settings -> Secrets** using TOML format:

```toml
GROQ_API_KEY = "your_groq_api_key"
ANAKIN_API_KEY = "your_anakin_api_key"
RAPIDAPI_KEY = "your_rapidapi_key"
```

After saving secrets, reboot the app from Streamlit Cloud.

## How It Works

1. `app.py` collects a search query from the user.
2. `agent.py` searches Devpost, Unstop, and Devfolio.
3. Results are merged and deduplicated.
4. `reasoning.py` sends compact result metadata to Groq and adds a `why` column.
5. `anakin_enrich.py` scrapes detail pages for the top results and attempts to extract team size.
6. `calendar_export.py` generates a downloadable `.ics` file from parsed deadlines.
7. `app.py` displays the ordered results table and the calendar download button.

## API Key Behavior

The app reads secrets through `config.py`:

- Local development: environment variables, root `.env`, or `clients/.env`
- Streamlit Cloud: `st.secrets`

If `GROQ_API_KEY` is missing, the app still runs and shows fallback text in the `why` column instead of crashing.

If `ANAKIN_API_KEY` is missing, detail-page enrichment is skipped.

If `RAPIDAPI_KEY` is missing, Unstop live calls will fail, but the app can still return Devpost and Devfolio results.

## Unstop Quota Protection

The Unstop client uses a RapidAPI wrapper with a limited free tier. To avoid accidental quota usage, live Unstop calls are disabled by default.

If `clients/unstop_cache.json` exists, the app reads cached Unstop data.

To deliberately spend one live Unstop request and populate the cache:

```bash
UNSTOP_LIVE_FETCH=1 python -m clients.unstop_client
```

## Deployment

1. Push the project to GitHub.
2. Create a Streamlit Cloud app pointing to `app.py`.
3. Add secrets in TOML format.
4. Reboot the app after changing secrets.

Useful deploy check:

```bash
git status -sb
git push origin main
```

If Streamlit is still showing old code, confirm that the app is deploying from the same GitHub repository and branch you pushed.

## Notes

- Devfolio uses an internal GraphQL API and may break if Devfolio changes its frontend API shape.
- Anakin enrichment runs only for the top shortlisted results to keep the app responsive.
- Calendar export skips deadlines it cannot parse instead of failing the whole download.
