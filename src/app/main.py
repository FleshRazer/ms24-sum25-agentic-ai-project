import argparse
from pathlib import Path

from app.graph import graph


def main(html_path, output_dir):
    document_html = None
    with open(html_path, mode="r", encoding="utf-8") as f:
        document_html = f.read()

    initial_state = {
        "html": document_html,
        "output_dir": output_dir,
        "output_filename": Path(html_path).stem,
    }
    _ = graph.invoke(initial_state)  # type: ignore


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("html_path", type=Path, help="Path to the HTML file")
    parser.add_argument(
        "output_dir", type=Path, help="Directory to save the Markdown output"
    )
    args = parser.parse_args()

    main(args.html_path, args.output_dir)
