from pydantic import BaseModel, Field
from typing import List, Optional
from langgraph.graph import MessagesState, StateGraph, START, END

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


def generate_search_queries(state):
    """
    Function to generate search queries based on the project description.
    """
    pass

def get_repos(state):
    """
    Tool function to retrieve GitHub repositories based on the search queries.
    """
    pass

def summarize_repos_info(state):
    """
    Function to summarize the information of the retrieved repositories.
    """
    pass



graph = StateGraph(SearchGithubAgentState)

graph.add_node("generate_search_queries", generate_search_queries)
graph.add_node("get_repos", get_repos)
graph.add_node("summarize_repos_info", summarize_repos_info)

graph.add_edge(START, "generate_search_queries")
graph.add_edge("generate_search_queries", "get_repos")
graph.add_edge("get_repos", "summarize_repos_info")
graph.add_edge("summarize_repos_info", END)

search_github_agent = graph.compile(name="search_github_agent")