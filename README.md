# 🤖 Babs Leye AI Assistant

A friendly AI-powered article summarization assistant built with Streamlit. **Babs Leye** helps you quickly understand articles from URLs and PDF documents with clear, engaging summaries.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

- **📰 Summarize from URL** — Paste any article link and get an instant summary
- **📄 Summarize from PDF** — Upload PDF documents for quick summarization
- **👤 Personality** — Babs Leye has a warm, approachable personality — helpful and never condescending
- **🛡️ Robust** — Graceful error handling and comprehensive logging
- **☁️ Deployable** — Ready for deployment on [Fly.io](https://fly.io)

## 📋 Prerequisites

- **Python 3.10+**
- **Google Gemini API Key** — Get a free key at [Google AI Studio](https://aistudio.google.com/app/apikey)

## 🚀 Installation

### 1. Clone or navigate to the project directory

```bash
cd bot
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

**Option A: Environment variable**

```bash
# Windows (PowerShell)
$env:GOOGLE_API_KEY = "your-api-key-here"

# Windows (CMD)
set GOOGLE_API_KEY=your-api-key-here

# macOS/Linux
export GOOGLE_API_KEY=your-api-key-here
```

**Option B: Use a `.env` file**

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## ▶️ Running the Application

### Local development

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

### Command-line options

```bash
# Run on a different port
streamlit run app.py --server.port 8080

# Run with server address binding (for Docker/remote access)
streamlit run app.py --server.address 0.0.0.0
```

## ☁️ Deployment on Fly.io

### Prerequisites

- [Fly.io account](https://fly.io/docs/speedrun/)
- [flyctl CLI](https://fly.io/docs/hands-on/install-flyctl/) installed

### Deploy steps

1. **Log in to Fly.io**

   ```bash
   fly auth login
   ```

2. **Launch the app** (first-time deployment)

   ```bash
   fly launch
   ```

   When prompted:
   - Choose an app name or accept the generated one
   - Select a region
   - Do **not** add a Postgres or Redis database

3. **Set your Google Gemini API key as a secret**

   ```bash
   fly secrets set GOOGLE_API_KEY=your-api-key-here
   ```

4. **Deploy**

   ```bash
   fly deploy
   ```

5. **Open your app**

   ```bash
   fly open
   ```

   Or visit `https://<your-app-name>.fly.dev`

### Updating your deployment

```bash
fly deploy
```

### Useful Fly.io commands

| Command | Description |
|---------|-------------|
| `fly status` | Check app status |
| `fly logs` | View application logs |
| `fly secrets list` | List secrets (values hidden) |
| `fly scale count 1` | Ensure at least 1 machine runs |

## 📁 Project Structure

```
bot/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container image for Fly.io
├── fly.toml            # Fly.io configuration
├── .env.example        # Example environment variables
├── .streamlit/
│   └── config.toml     # Streamlit configuration
├── babs_assistant.log  # Application logs (created at runtime)
└── README.md           # This file
```

## 📝 Logging

The application writes logs to:

- **Console** — stdout (visible in `fly logs` when deployed)
- **File** — `babs_assistant.log` in the project directory

Log format: `timestamp - logger_name - level - message`

## ⚠️ Error Handling

The app handles common errors gracefully:

- **Missing API key** — Clear instructions for configuration
- **Invalid or inaccessible URLs** — Friendly error messages
- **Unreadable PDFs** — Notifies if PDF is scanned/image-based
- **Gemini rate limits** — Suggests retrying later
- **Network issues** — Descriptive error feedback

## 🔧 Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` or `GEMINI_API_KEY` | Yes | Your Google Gemini API key for summarization |

## 📜 License

MIT License — Built with ❤️ by Babs Leye
