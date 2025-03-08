# RAG Chat Interface

A Retrieval-Augmented Generation (RAG) system that uses Wikipedia articles to provide informed responses to user queries. The system features a clean web interface and uses the Llama-2 model for generating responses.

## Features

- Real-time Wikipedia article retrieval and processing
- Vector-based semantic search for relevant context
- LLM-powered response generation using Llama-2
- Clean and responsive web interface
- Automatic source citation with links to Wikipedia articles

## Prerequisites

- Python 3.10 or higher
- Virtual environment (recommended)
- Llama-2 model file (7B-chat quantized version)
- Wikipedia API access token

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd rag-app
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` with your settings:
     - Generate a secure API token (you can use `openssl rand -hex 32`)
     - Set up your Wikipedia API credentials (see below)
     - Adjust other settings as needed

5. Create necessary directories:
```bash
mkdir -p models data app/static
```

6. Download the Llama-2 model:
   - Visit [TheBloke's Hugging Face page](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML)
   - Download the `llama-2-7b-chat.ggmlv3.q4_0.bin` model
   - Place it in the `models` directory

## Getting API Tokens

### Wikipedia API Access
1. Visit [Wikimedia API Portal](https://api.wikimedia.org/wiki/Main_Page)
2. Create an account and log in
3. Go to [Create Credentials](https://api.wikimedia.org/wiki/Special:AppManagement)
4. Create a new application:
   - Set a meaningful app name and description
   - Request the 'basic' scope
   - Save your credentials
5. Copy the access token to your `.env` file

### User Agent Setup
Follow [Wikimedia's User-Agent policy](https://meta.wikimedia.org/wiki/User-Agent_policy):
- Use a descriptive User-Agent string
- Include your application name and version
- Add your website (or GitHub repo) and contact email
- Example: `'MyApp/1.0 (https://github.com/username/repo; email@example.com)'`

## Configuration

The application can be configured through:
- `.env`: Environment variables and secrets (copy from `.env.example`)
- `app/config.py`: General application settings

Key configuration options:
- `MAX_ARTICLES`: Number of Wikipedia articles to fetch per query (default: 3)
- `CHUNK_SIZE`: Size of text chunks for processing (default: 500)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 50)
- `MODEL_MAX_TOKENS`: Maximum tokens for LLM response (default: 512)

## Usage

1. Start the server:
```bash
cd rag-app
uvicorn app.main:app --reload --port 8001
```

2. Open your browser and navigate to:
```
http://localhost:8001
```

3. Start asking questions! The system will:
   - Search Wikipedia for relevant articles
   - Process and index the content
   - Generate an informed response
   - Provide source links to the original articles

## Project Structure

```
rag-app/
├── app/
│   ├── templates/
│   │   └── index.html
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── data_ingestion.py
│   ├── model.py
│   └── main.py
├── models/
│   └── (Llama-2 model files)
├── data/
│   └── (Vector store data)
├── requirements.txt
├── .env.example
├── .env
└── README.md
```

## Security Notes

- Never commit the `.env` file or model files to version control
- Keep your API tokens secure
- The application uses token-based authentication for API endpoints
- Regularly rotate your API tokens
- Monitor your API usage to stay within rate limits

## License

[Your chosen license]

## Contributing

[Your contribution guidelines] 