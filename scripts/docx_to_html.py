import argparse
import glob
import os

import mammoth
from bs4 import BeautifulSoup
from tidylib import tidy_document

parser = argparse.ArgumentParser(
    description="Convert .docx files to HTML, remove <img> tags, and clean with tidy."
)
parser.add_argument("input_dir", help="Directory containing input .docx files")
parser.add_argument("output_dir", help="Directory to save output HTML files")
args = parser.parse_args()

os.makedirs(args.output_dir, exist_ok=True)

for docx_file in glob.glob(os.path.join(args.input_dir, "*.docx")):
    base_name = os.path.splitext(os.path.basename(docx_file))[0]
    output_html = os.path.join(args.output_dir, f"{base_name}.html")

    with open(docx_file, "rb") as docx:
        result = mammoth.convert_to_html(docx)
        html_content = result.value  # Get the HTML content

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

    with open(output_html, "w", encoding="utf-8") as file:
        file.write(tidy_html)

    print(f"Processed {docx_file} -> {output_html}")
