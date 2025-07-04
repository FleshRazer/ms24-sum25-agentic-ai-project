import re
from pathlib import Path

from langchain.output_parsers import (
    PydanticOutputParser,
)
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph
from typing_extensions import TypedDict

from app.schemas import ItemList

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")


class GraphState(TypedDict):
    html: str | None
    markdown: str | None
    output_dir: Path
    output_filename: str


def conv_markdown(state: GraphState) -> GraphState:
    prompt = PromptTemplate.from_template(
        "Convert the HTML document into Markdown. Output should not contain any tables. "
        "Each table from the original document must be decomposed using headings. "
        "Your final output should be inside a markdown code block.\n"
        "```html\n"
        "{document_html}\n"
        "```"
    )

    chain = prompt | llm
    result = chain.invoke({"document_html": state["html"]})

    pattern = r"```markdown\s*(.*?)\s*```"
    match = re.search(pattern, result.text(), re.DOTALL)
    if match is not None:
        content = match.group(1).strip()

    return {"markdown": content}  # type: ignore


def save_markdown(state: GraphState) -> GraphState:
    if state["markdown"] is not None:
        with open(
            state["output_dir"] / "md" / (state["output_filename"] + ".md"), mode="w"
        ) as f:
            f.write(state["markdown"])

    return {}  # type: ignore


def parse_items(state: GraphState) -> GraphState:
    parser = PydanticOutputParser(pydantic_object=ItemList)
    prompt = PromptTemplate(
        template=(
            "Extract structured item data from the following technical specification."
            "```markdown\n"
            "{document_markdown}\n"
            "```\n"
            "{format_instructions}"
        ),
        input_variables=["document"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | llm | parser
    result = chain.invoke({"document_markdown": state["markdown"]})

    with open(
        state["output_dir"] / "items" / (state["output_filename"] + ".json"), mode="w"
    ) as f:
        f.write(result.model_dump_json(indent=2, by_alias=True))

    return {}  # type: ignore


graph_builder = StateGraph(GraphState)

graph_builder.add_node("conv_markdown", conv_markdown)
graph_builder.add_node("save_markdown", save_markdown)
graph_builder.add_node("parse_items", parse_items)

graph_builder.add_edge("conv_markdown", "save_markdown")
graph_builder.add_edge("conv_markdown", "parse_items")

graph_builder.set_entry_point("conv_markdown")

graph = graph_builder.compile()
