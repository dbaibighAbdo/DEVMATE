from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from typing import List
from langgraph.prebuilt import ToolNode, tools_condition, create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import BaseTool
from dotenv import load_dotenv

load_dotenv()


def build_agent_graph(tools: List[BaseTool] = []):

    system_prompt ="""
    You are a coding assistant. Your role is to assist users by finding GitHub repositories that match their needs, and build their project step-by-step based on the choosen repository.

    TASKS:
        1. Always think step-by-step before making a decision.
        2. If the request is unclear or incomplete, ask concise, targeted clarifying questions before taking any action.
        3. Analyze the project description given by the user.
        4. Create a precise, relevant, and effective search query for GitHub.
        3. Use the relevent tool to retrieve up to 5 repositories (with more stars).
        4. If no repositories are found:
            - Refine the search query and retry (maximum of 2 additional attempts).
        5. If after 3 total attempts no repositories are found:
            - Inform the user that no relevant repositories were found.
        6. Present the found repositories in a clear, structured Markdown format.
            - **Repository Name**: <repo_name>
            - **Owner**: <repo_owner>
            - **Description**: <repo_description>
            - **Stars**: <repo_stars>
            - **Language**: <language>
            - **Open Issues**: <repo_open_issues>
            - **Created At**: <repo_created_at>
            - **Updated At**: <repo_updated_at>
            - **URL**: <repo_url>

        7. Ask the user to choose one of the repositories by its number for further assistance in building the project.
        8. If the user wants to change the project description or tech stack, return to step 3 with updated details.
        9. If the user wants to change the repository, return to step 3.
        10. After the user selects a repository, give a brief summary and the architecture of the chosen repository.
        11. Use the most relevent tool to assist the user in building the project step-by-step based on the choosen repository.

    NOTES:
        - Never invent or guess repository details.
        - Ensure each repository is listed separately and numbered in order.

    TOOLS:
        {tools}
    """

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    if tools:
        tools_json = [tool.model_dump_json(include=["name", "description"]) for tool in tools]
        system_prompt = system_prompt.format(
            tools="\n".join(tools_json)
            )

    def assistant(state: MessagesState) -> MessagesState:
        response = create_react_agent(
            model=llm,
            instructions=system_prompt,
            tools=tools,
            name="Assistant"
        ).invoke(state.messages)
        state.messages.append(response)
        return state

    builder = StateGraph(MessagesState)

    builder.add_node("Assistant", assistant)
    builder.add_node(ToolNode(tools))

    builder.add_edge(START, "Assistant")
    builder.add_conditional_edges(
        "Assistant",
        tools_condition,
    )
    builder.add_edge("tools", "Assistant")
    builder.add_edge("Assistant", END)

    return builder.compile(checkpointer=MemorySaver())


# visualize graph
if __name__ == "__main__":
    from IPython.display import display, Image
    
    graph = build_agent_graph()
    display(Image(graph.get_graph().draw_mermaid_png()))