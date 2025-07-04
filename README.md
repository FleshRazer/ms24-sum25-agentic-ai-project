# ms24-sum25-agentic-ai-project

## Getting Started

Install `uv`:

```bash
pip3 install uv
```

Install dependencies:

```bash
uv sync
```

Run agent:

```bash
export GOOGLE_API_KEY={your-key-here}
uv run python3 src/app/main.py {input-html} {output-dir}
```
