import re
from pathlib import Path

from langchain.output_parsers import (
    PydanticOutputParser,
)
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler
from langgraph.graph import StateGraph
from typing_extensions import TypedDict

from app.schemas import ItemList
from app.settings import settings

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", google_api_key=settings.GOOGLE_API_KEY
)


class GraphState(TypedDict):
    html: str | None
    markdown: str | None
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
    result = chain.invoke({"document_html": state["html"]})

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
    result = chain.invoke({"document_markdown": state["markdown"]})

    with open(
        state["output_dir"] / "items" / (state["output_filename"] + ".json"), mode="w"
    ) as f:
        f.write(result.model_dump_json(indent=2, by_alias=True))

    return {}  # type: ignore


graph_builder = StateGraph(GraphState)

graph_builder.add_node("validate_content", validate_content)
graph_builder.add_node("conv_markdown", conv_markdown)
graph_builder.add_node("save_markdown", save_markdown)
graph_builder.add_node("parse_items", parse_items)

graph_builder.add_edge("validate_content", "conv_markdown")
graph_builder.add_edge("conv_markdown", "save_markdown")
graph_builder.add_edge("conv_markdown", "parse_items")

graph_builder.set_entry_point("validate_content")

langfuse = Langfuse(
    secret_key=settings.LANGFUSE_SECRET_KEY,
    public_key=settings.LANGFUSE_PUBLIC_KEY,
    host="http://localhost:3000",
)

if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")
else:
    print("Authentication failed. Please check your credentials and host.")

langfuse_handler = CallbackHandler()

graph = graph_builder.compile().with_config({"callbacks": [langfuse_handler]})
