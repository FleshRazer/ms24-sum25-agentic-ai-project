import argparse
import mimetypes
from pathlib import Path

import mammoth
from bs4 import BeautifulSoup
from tidylib import tidy_document

from app.graph import graph
from app.settings import settings

def read_docx_as_html(docx_path):
    with open(docx_path, mode="rb") as f:
        result = mammoth.convert_to_html(f)
    html_content = result.value  # Get the HTML content

    # Remove images
    soup = BeautifulSoup(html_content, "html.parser")
    for img in soup.find_all("img"):
        img.decompose()
    modified_html = str(soup)

    tidy_html, errors = tidy_document(
        modified_html,
        options={
            "indent": "auto",  # Match -indent for automatic indentation
            "wrap": 0,  # No wrapping, same as -wrap 0
            "quiet": True,  # Suppress non-error messages, same as -quiet
            "char-encoding": "utf8",  # Use UTF-8 encoding
            "output-html": True,  # Ensure HTML output (not XHTML)
            "force-output": True,  # Output even if errors
            "tidy-mark": False,  # Avoid adding Tidy generator meta tag
            "show-warnings": False,  # Suppress warnings to align with -quiet
            "newline": "LF",  # Use Unix-style line endings for consistency
        },
    )
    return tidy_html


def is_docx(docx_path):
    mime_type, _ = mimetypes.guess_type(docx_path)
    return (
        mime_type
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


def main(docx_path, output_dir):
    if not is_docx(docx_path):
        print("Provided file is not .docx document!")
        return

    document_html = read_docx_as_html(docx_path)
    output_filename = Path(docx_path).stem

    with open(output_dir / "html" / (output_filename + ".html"), mode="w") as f:
        f.write(document_html)

    initial_state = {
        "html": document_html,
        "output_dir": output_dir,
        "output_filename": output_filename,
    }

    try:
        _ = graph.invoke(initial_state)  # type: ignore
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--docx_path", type=Path, help="Path to the DOCX file")
    parser.add_argument("--output_dir", type=Path, help="Directory to save the outputs")
    parser.add_argument("--llm-provider", type=str, default='google', choices=['google', 'mistral'], help="LLM provider to use (default: google)")
    args = parser.parse_args()

    settings.LLM_PROVIDER = args.llm_provider
    main(args.docx_path, args.output_dir)
