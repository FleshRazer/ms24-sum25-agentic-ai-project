from typing import List
import json
from pydantic import ValidationError
from app.schemas import ItemList
import argparse
from pathlib import Path

def generate_technical_specifications(items_json: List[ItemList], md_files: List[str], item_names: List[str]) -> str:
    """
    Generate technical specifications based on provided items JSON, markdown files, and item names.

    This function currently returns an empty string as per requirements. In the future, it can be expanded to generate
    specifications using the inputs.

    :param items_json: A JSON string representing a list of items.
    :param md_files: A list of markdown file paths or contents.
    :param item_names: A list of item names to generate specifications for.
    :return: Generated technical specifications (currently an empty string).
    """
    print(items_json)
    print(md_files)
    print(item_names)
    # TODO: Implement generation logic using md_files and item_names

    return 'test'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate technical specifications.")
    parser.add_argument("--items_dir", type=Path, required=True, help="Path to directory with ItemList JSON files")
    parser.add_argument("--md_dir", type=Path, required=True, help="Path to directory with MD files")
    parser.add_argument("--output_md", type=Path, required=True, help="Path to output MD file")
    args = parser.parse_args()

    # Default item names for now
    item_names = ["default_item1"]  # Set some default values

    items_json = json.dumps([json.loads(f.read_text()) for f in args.items_dir.glob("*.json")])
    md_files = [str(f) for f in args.md_dir.glob("*.md")]

    # Call the function
    result = generate_technical_specifications(items_json, md_files, item_names)

    # Write to output_md
    args.output_md.write_text(result)

# Running example from CLI
# python src/app/generator.py --items_dir data/kamaz_energo/items/gemini-2.5-pro/ --md_dir data/kamaz_energo/md/gemini-2.5-pro/ --output_md data/kamaz_energo/generated.md
