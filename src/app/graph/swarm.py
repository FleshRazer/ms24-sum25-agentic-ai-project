from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool, create_swarm

from app.llm import llm

transfer_to_reviewer = create_handoff_tool(
    agent_name="reviewer",
)
transfer_to_extractor = create_handoff_tool(
    agent_name="extractor",
)

extractor = create_react_agent(
    model=llm,
    tools=[transfer_to_reviewer],
    prompt=(
        "You are an extractor agent. Your task is to extract the item list from the procurement technical specification. Always pass the list to the reviewer agent before finishing the work. If reviewer agent has no objections, then provide the final item list.\n\n"
        "This is the list of the things to be extracted (some of them might be missing in the technical specification):\n\n"
        "- Наименование\n"
        "- Марка\n"
        "- Тип\n"
        "- Количество\n"
        "- Единица измерения\n"
        "- Наличие аналогов\n"
        "- Код ОКДП2\n"
        "- Сведения о новизне\n"
        "- Область применения\n"
        "- Условия эксплуатации\n"
        "- Технические требования\n"
        "- Комплектация\n"
        "- Требования по правилам сдачи и приемки\n"
        "- Требования к транспортированию\n"
        "- Требования к хранению"
    ),
    name="extractor",
)

reviewer = create_react_agent(
    model=llm,
    tools=[transfer_to_extractor],
    prompt=(
        "You are a reviewer agent. Your task is to review the extracted item list from the procurement technical specification and provide feedback. Check if anything is missing from the original technical specification, if there are any typos or other kinds of errors. Always transfer to extractor agent, even if there are no issues.\n\n"
        "This is the list of the things to be extracted (some of them might be missing in the technical specification):\n\n"
        "- Наименование\n"
        "- Марка\n"
        "- Тип\n"
        "- Количество\n"
        "- Единица измерения\n"
        "- Наличие аналогов\n"
        "- Код ОКДП2\n"
        "- Сведения о новизне\n"
        "- Область применения\n"
        "- Условия эксплуатации\n"
        "- Технические требования\n"
        "- Комплектация\n"
        "- Требования по правилам сдачи и приемки\n"
        "- Требования к транспортированию\n"
        "- Требования к хранению\n\n"
        "Your feedback should be concise, provide a list of issues or tell that everything is fine."
    ),
    name="reviewer",
)

checkpointer = InMemorySaver()

swarm = create_swarm(
    agents=[extractor, reviewer], default_active_agent="extractor"
).compile(checkpointer=checkpointer)
