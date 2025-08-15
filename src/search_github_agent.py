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
    url: str = Field(description="The URL of the repository.")
    stars: int = Field(description="The number of stars the repository has received.")
    forks: int = Field(description="The number of forks of the repository.")
    created_at: str = Field(description="The date and time when the repository was created.")
    open_issues: int = Field(description="The number of open issues in the repository.")
    updated_at: str = Field(description="The date and time when the repository was last updated.")
    readme: Optional[str] = Field(description="The README content of the repository.")


class SearchGithubAgentState(MessagesState):
    project_description: str = Field(description="Project description provided by the user.")
    search_querie: str = Field(description="Search query generated based on the project description.")
    repos: List[Repository] = Field(description="List of repositories retrieved from GitHub based on the search queries.")




search_github_agent_prompt = """
You are a github searcher agent that helps the supervisor search for repositories on GitHub based on their project description.

Your tasks include:
1. Analyzing the project description provided by the supervisor.
2. Generating a well-structured search query for GitHub.
3. Retrieving first 5 (5 as a maximum) repositories from GitHub based on the search query using {get_repositories_tool}.
4. If no repositories are found, generate a new search query and repeat the process 2 times maximum.
5. If no repositories are found after 3 attempts, inform the supervisor that no relevant repositories were found.

General Guidelines:
- Always clarify user requests before proceeding with actions.
- Think step-by-step before acting.
- When generating a search query, ensure it is relevant to the project description.
- Use the {get_repositories_tool} to retrieve repositories based on the generated search query.
- Present the retrieved repositories in a clear and structured format.
- Use markdown formatting for better readability, but ensure the content remains factual and relevant to the supervisor's request.

The repositories should be presented like this:
    1. **Repository Name**: [repo_name](repo_url)
        - **Owner**: repo_owner
        - **Description**: repo_description
        - **Stars**: repo_stars
        - **Forks**: repo_forks
        - **Open Issues**: repo_open_issues
        - **Created At**: repo_created_at
        - **Updated At**: repo_updated_at


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
    llm="gpt-4",
    tools=[get_repositories_tool],
    prompt=search_github_agent_prompt,
    state_class=SearchGithubAgentState
).compile(name="search_github_agent")
