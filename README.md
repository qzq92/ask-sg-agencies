# SG Open Data Agentic Dataset Recommender

A multi-agent AI system that recommends datasets from Singapore's Open Data Portal (data.gov.sg) based on user problems. Uses a meta-controller supervisor architecture with 10 category-specific subagents running in parallel.

## Architecture

- **Supervisor Agent**: Classifies user queries and routes to 1–3 relevant category agents. Recognizes Singapore government agency names (HDB, LTA, MOH, etc.) and maps them to appropriate categories.
- **Category Agents**: Arts & Culture, Education, Economy, Environment, Geospatial, Housing, Health, Social, Transport, Real-time APIs. Run in parallel for faster responses.
- **Synthesizer**: Aggregates recommendations into a unified response with dataset links.

All agents use OpenAI GPT-5.1 for reasoning and tool execution.

### Tools Available to Agents

- `get_dataset_metadata`: Fetch detailed schema for a specific dataset
- `search_datasets`: Search datasets by keywords with optional agency filter
- `list_datasets_by_agency`: List all datasets from a specific agency

## Setup

1. Create a `.env` file with:
   ```
   OPENAI_API_KEY=your_openai_api_key
   LANGSMITH_API_KEY=your_langsmith_key  # optional, for tracing
   ```

2. Install dependencies with [uv](https://docs.astral.sh/uv/):
   ```bash
   uv sync
   ```

3. Run the Streamlit app:
   ```bash
   uv run streamlit run app.py
   ```

## Project Structure

```
ask-sg-agencies/
├── app.py                 # Streamlit entrypoint
├── agent/                 # Supervisor, synthesizer, category agent runner
├── config/                # LLM configuration (OpenAI)
├── data/                  # Agency-to-category mapping
├── prompt/                # System prompts for each agent
├── tools/                 # Dataset search and metadata tools
└── src/                   # State, graph, agent runner
```

## Supported Agencies

The system recognizes mentions of Singapore government agencies and routes queries accordingly:

| Category | Agencies |
|----------|----------|
| Housing | HDB, URA, SLA |
| Transport | LTA, SMRT, SBS Transit |
| Health | MOH, HPB, HSA |
| Environment | NEA, PUB, NParks |
| Education | MOE, SkillsFuture, SSG |
| Economy | ACRA, EDB, ESG, MAS, IRAS, MOM, CPF |
| Social | MSF, NCSS |
| Arts & Culture | NAC, NHB, NLB, MCCY |
| Geospatial | SLA, OneMap |
| Real-time APIs | GovTech, IMDA |
