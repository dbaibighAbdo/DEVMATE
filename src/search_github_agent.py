from pydantic import BaseModel, Field
from typing import List, Optional
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent, ToolNode
from langchain_core.tools import tool

class Repository(BaseModel):
    id: int = Field(description="The unique identifier of the repository.")
    name: str = Field(description="The name of the repository.")
    owner: str = Field(description="The owner of the repository.")
    description: str = Field(description="A brief description of the repository.")
    main_language: Optional[str] = Field(description="The primary programming language used in the repository.")
    url: str = Field(description="The URL of the repository.")
    stars: int = Field(description="The number of stars the repository has received.")
    forks: int = Field(description="The number of forks of the repository.")
    created_at: str = Field(description="The date and time when the repository was created.")
    open_issues: int = Field(description="The number of open issues in the repository.")
    updated_at: str = Field(description="The date and time when the repository was last updated.")


class SearchGithubAgentState(MessagesState):
    project_description: str = Field(description="Project description provided by the user.")
    search_querie: str = Field(description="Search query generated based on the project description.")
    repos: List[Repository] = Field(description="List of repositories retrieved from GitHub based on the search queries.")



search_github_agent_prompt = """
You are the `search_github_agent`. Your role is to assist the SUPERVISOR by finding GitHub repositories that match the provided project description.

TASKS:
    1. Analyze the project description given by the SUPERVISOR.
    2. Create a precise, relevant, and effective search query for GitHub.
    3. Use {get_repositories_tool} to retrieve up to 5 repositories (maximum).
    4. If no repositories are found:
        - Refine the search query and retry (maximum of 2 additional attempts).
    5. If after 3 total attempts no repositories are found:
        - Inform the SUPERVISOR that no relevant repositories were found.

GENERAL GUIDELINES:
    - Always think step-by-step before acting.
    - The search query must be closely aligned with the project description.
    - Clarify unclear requests before proceeding.
    - Present results exactly as returned by {get_repositories_tool} without altering factual data.
    - Always use Markdown for readability.
    - Keep descriptions factual, relevant, and concise.

OUTPUT FORMAT:
Present the repositories in the following exact structure:

    1. **Repository Name**: [<repo_name>](<repo_url>)
        - **Owner**: <repo_owner>
        - **Description**: <repo_description>
        - **Stars**: <repo_stars>
        - **Forks**: <repo_forks>
        - **Open Issues**: <repo_open_issues>
        - **Created At**: <repo_created_at>
        - **Updated At**: <repo_updated_at>

NOTES:
    - Never invent or guess repository details.
    - Ensure each repository is listed separately and numbered in order.
"""


@tool
def get_repositories(state):
    """
    Tool function to retrieve GitHub repositories based on the search queries.
    """
    pass

get_repositories_tool = ToolNode(name="get_repositories", func=get_repositories)

search_github_agent = create_react_agent(
    name="search_github_agent",
    description="A GitHub search agent that helps the supervisor search for repositories based on project description.",
    model="gpt-4o",
    tools=[get_repositories_tool],
    prompt=search_github_agent_prompt,
    state_class=SearchGithubAgentState
).compile(name="search_github_agent")
