# SG Open Data Agentic Dataset Recommender

A multi-agent AI system that recommends datasets from Singapore's Open Data Portal (data.gov.sg) based on user problems. Uses a meta-controller supervisor architecture with 10 category-specific subagents.

## Architecture

- **Supervisor Agent**: Classifies user queries and routes to 1–3 relevant category agents
- **Category Agents**: Arts & Culture, Education, Economy, Environment, Geospatial, Housing, Health, Social, Transport, Real-time APIs
- **Synthesizer**: Aggregates recommendations into a unified response with dataset links

Each subagent uses Perplexity's built-in web search to sieve through datasets in its assigned category on data.gov.sg.

## Setup

1. Create a `.env` file with:
   ```
   PPLX_API_KEY=your_perplexity_api_key
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
├── agent/                 # Supervisor, synthesizer, and 10 category subagents
├── config/                # Configuration (LLM, env)
├── prompt/                # System prompts for each agent
└── src/                   # State, graph, tools
```
