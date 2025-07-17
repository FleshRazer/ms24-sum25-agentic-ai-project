# ms24-sum25-agentic-ai-project
## Getting Started


Install `uv`:

```bash
pip3 install uv
```

Install dependencies:

```bash
uv sync
uv pip install -e .
```

Set environment variables (see `.example.env` for details) or use `.env` file:

```bash
export GOOGLE_API_KEY={your-google-key}  # For Google provider
export MISTRAL_API_KEY={your-mistral-key}  # For Mistral provider
```

Run agent:

```bash
uv run python3 src/app/main.py --docx_path {input-html} --output_dir {output-dir} --llm-provider {google,mistral}
```

Example command for running agent with Google provider:

```bash
uv run python3 src/app/main.py --docx_path data/kamaz_energo/docx/001.docx --output_dir data/kamaz_energo/ --llm-provider google
```
