# Google Analytics 4 Report Generator

An automated system that generates comprehensive analytics reports using GA4 data and LLMs.

## Features

- Fetches data from Google Analytics 4
- Analyzes traffic sources, user behavior, and geographic distribution
- Generates insights using GPT-4
- Provides actionable recommendations
- Compiles structured reports

## Prerequisites

- Python 3.9+
- Google Analytics 4 account with API access
- OpenAI API key
- Required Python packages (see requirements.txt)

## Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd AA2
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables in `.env`:

```
GA_PROPERTY_ID=your_property_id
GA_CLIENT_ID=your_client_id
GA_CLIENT_SECRET=your_client_secret
GA_REFRESH_TOKEN=your_refresh_token
OPENAI_API_KEY=your_openai_key
```

## Usage

Run the main script:

```bash
python main.py
```

The script will:

1. Fetch data from your GA4 property
2. Analyze the data using GPT-4
3. Generate insights
4. Provide recommendations
5. Compile a final report

## Project Structure

```
AA2/
├── main.py                # Entry point
├── src/
│   ├── flows/            # LangGraph workflow
│   ├── nodes/            # Processing nodes
│   ├── connectors/       # External service connectors
│   ├── models/           # Data models
│   ├── prompts/          # LLM prompts
│   └── utils/            # Utility functions
├── config/               # Configuration files
└── notebooks/           # Jupyter notebooks for testing
```

## Configuration

Edit `config/config.yaml` to customize:

- GA4 metrics and dimensions
- Report structure
- LLM parameters
- Logging settings

## Development

For development and testing:

1. Use the provided Jupyter notebooks in `notebooks/`
2. Run individual components using the notebook environment
3. Modify prompts in `src/prompts/` to adjust LLM behavior
4. Update metrics/dimensions in `config/config.yaml` as needed

## Error Handling

The system includes comprehensive error handling and logging:

- Check logs for detailed error information
- Common issues include:
  - Invalid GA4 credentials
  - API rate limits
  - Network connectivity problems

## License

[Your chosen license]
