import re
from pathlib import Path

from langchain.output_parsers import (
    PydanticOutputParser,
)
from langchain.prompts import PromptTemplate
from langgraph.graph import StateGraph
from typing_extensions import TypedDict

from app.callbacks import callbacks
from app.graph.swarm import swarm
from app.llm import llm, model
from app.schemas import ItemList
from app.settings import settings


class GraphState(TypedDict):
    document_html: str | None
    document_markdown: str | None
    items_markdown: str | None
    output_dir: Path
    output_filename: str


def validate_content(state: GraphState) -> GraphState:
    from pydantic import BaseModel, Field

    class DocumentValidationResult(BaseModel):
        """Result of document validation."""

        is_valid: bool = Field(...)

    parser = PydanticOutputParser(pydantic_object=DocumentValidationResult)
    prompt = PromptTemplate(
        template=(
            "Check if the following document is a procurement technical specification.\n\n"
            "```html\n"
            "{document_html}\n"
            "```\n"
            "{format_instructions}"
        ),
        input_variables=["document"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | llm | parser
    result = chain.invoke({"document_html": state["document_html"]})

    if not result.is_valid:
        raise ValueError(
            "Provided document is not a procurement technical specification!"
        )

    return {}  # type: ignore


def conv_markdown(state: GraphState) -> GraphState:
    prompt = PromptTemplate.from_template(
        "Convert the HTML document into Markdown. Output should not contain any tables. "
        "Each table from the original document must be decomposed using headings. "
        "Your final output should be inside a markdown code block.\n\n"
        "```html\n"
        "{document_html}\n"
        "```"
    )

    chain = prompt | llm
    result = chain.invoke({"document_html": state["document_html"]})

    pattern = r"```markdown\s*(.*?)\s*```"
    match = re.search(pattern, result.text(), re.DOTALL)
    if match is not None:
        content = match.group(1).strip()

    return {"document_markdown": content}  # type: ignore


def save_markdown(state: GraphState) -> GraphState:
    if state["document_markdown"] is not None:
        write_path = (
            state["output_dir"] / "md" / model / (state["output_filename"] + ".md")
        )
        write_path.parent.mkdir(parents=True, exist_ok=True)
        with open(write_path, mode="w") as f:
            f.write(state["document_markdown"])

    return {}  # type: ignore


def parse_items(state: GraphState) -> GraphState:
    parser = PydanticOutputParser(pydantic_object=ItemList)
    prompt = PromptTemplate(
        template=(
            "Extract structured item data from the following technical specification.\n\n"
            "```markdown\n"
            "{document_markdown}\n"
            "```\n"
            "{format_instructions}"
        ),
        input_variables=["document"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | llm | parser
    markdown = (
        state["items_markdown"]
        if settings.ENABLE_REVIEWER
        else state["document_markdown"]
    )
    result = chain.invoke({"document_markdown": markdown})

    write_path = (
        state["output_dir"] / "items" / model / (state["output_filename"] + ".json")
    )
    write_path.parent.mkdir(parents=True, exist_ok=True)
    with open(write_path, mode="w") as f:
        f.write(result.model_dump_json(indent=2, by_alias=True))

    return {}  # type: ignore


if settings.ENABLE_REVIEWER:

    def call_swarm(state: GraphState):
        swarm_state = swarm.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            f"Procurement technical specification:\n\n"
                            f"```markdown\n"
                            f"{state['document_markdown']}\n"
                            f"```\n"
                        ),
                    }
                ],
            },
            {"configurable": {"thread_id": "1"}},
        )

        return {"items_markdown": swarm_state["messages"][-1].content}

    workflow = StateGraph(GraphState)

    workflow.add_node("validate_content", validate_content)
    workflow.add_node("conv_markdown", conv_markdown)
    workflow.add_node("save_markdown", save_markdown)
    workflow.add_node("call_swarm", call_swarm)
    workflow.add_node("parse_items", parse_items)

    workflow.add_edge("validate_content", "conv_markdown")
    workflow.add_edge("conv_markdown", "save_markdown")
    workflow.add_edge("conv_markdown", "call_swarm")
    workflow.add_edge("call_swarm", "parse_items")

    workflow.set_entry_point("validate_content")

else:
    workflow = StateGraph(GraphState)

    workflow.add_node("validate_content", validate_content)
    workflow.add_node("conv_markdown", conv_markdown)
    workflow.add_node("save_markdown", save_markdown)
    workflow.add_node("parse_items", parse_items)

    workflow.add_edge("validate_content", "conv_markdown")
    workflow.add_edge("conv_markdown", "save_markdown")
    workflow.add_edge("conv_markdown", "parse_items")

    workflow.set_entry_point("validate_content")

graph = workflow.compile().with_config({"callbacks": callbacks})
