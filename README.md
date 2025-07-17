# Agentic Procurement Parsing

This project is a part of work automation around procurements. It addresses the extraction of structured item information from technical specifications for subsequent analysis and use. It is built around LangGraph framework and provides users with a pipeline which takes .docx technical specification as input and outputs a list of items in JSON format. Alongside with the item specifications, it produces LLM friendly representations of technical specification in HTML and Markdown formats.

## Getting Started

### Prepare environment

```bash
pip3 install uv
uv sync
uv pip install -e .
```

### Update `.env` file

- Set Google AI Studio or Mistral API key
- Set Langfuse keys if you are going to use it

### Run the agent

```bash
uv run python3 src/app/main.py \
    --docx_path=data/kamaz_energo/docx/001.docx \
    --output_dir=data/kamaz_energo \
    --llm-provider=google
```

## Self-host Langfuse using Docker (Optional)

Get a copy of the latest Langfuse repository:

```
git clone https://github.com/langfuse/langfuse.git
cd langfuse
```

Update the secrets in the docker-compose.yml and then run the langfuse docker compose using:

```
docker compose up
```

Full instruction: https://langfuse.com/self-hosting/docker-compose
