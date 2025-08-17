from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import httpx

load_dotenv("OPENAI_API_KEY", "HEADERS")

model = ChatOpenAI(model="gpt-4o")

search_github_agent_prompt = """
You are the `search_github_agent`. Your role is to assist the SUPERVISOR by finding GitHub repositories that match the provided project description.

TASKS:
    1. Analyze the project description given by the SUPERVISOR.
    2. Create a precise, relevant, and effective search query for GitHub.
    3. Use {get_repositories} to retrieve up to 5 repositories (maximum).
    4. If no repositories are found:
        - Refine the search query and retry (maximum of 2 additional attempts).
    5. If after 3 total attempts no repositories are found:
        - Inform the SUPERVISOR that no relevant repositories were found.

GENERAL GUIDELINES:
    - Always think step-by-step before acting.
    - The search query must be closely aligned with the project description.
    - Clarify unclear requests before proceeding.
    - Present results exactly as returned by {get_repositories} without altering factual data.
    - Always use Markdown for readability.
    - Keep descriptions factual, relevant, and concise.

OUTPUT FORMAT:
Present the repositories in the following exact structure:

    1. **Repository Name**: <repo_name>
        - **Owner**: <repo_owner>
        - **Description**: <repo_description>
        - **Stars**: <repo_stars>
        - **Language**: <language>
        - **Open Issues**: <repo_open_issues>
        - **Created At**: <repo_created_at>
        - **Updated At**: <repo_updated_at>
        - **URL**: <repo_url>

NOTES:
    - Never invent or guess repository details.
    - Ensure each repository is listed separately and numbered in order.
"""

@tool
def get_repositories(search_query: str) -> dict:
    """
    Search GitHub repositories based on a query from state["search_query"].

    Args:
        state (dict): Dictionary containing a key "search_query".

    Returns:
        list: Top 5 repositories with name, URL, and description.
    """
    query = search_query
    if not query:
        raise ValueError("no 'search_query' provided.")

    url = "https://api.github.com/search/repositories"
    params = {"q": query, "sort": "stars", "order": "desc", "per_page": 5}

    with httpx.Client() as client:
        response = client.get(url, params=params, headers="HEADERS")

    if response.status_code != 200:
        raise Exception(f"GitHub API error: {response.status_code}, {response.text}")

    items = response.json().get("items", [])

    results = [
        {
            "name": repo["full_name"],
            "url": repo["html_url"],
            "owner": repo["owner"]["login"],
            "stars": repo["stargazers_count"],
            "language": repo["language"],
            "description": repo["description"],
            "created_at": repo["created_at"],
            "updated_at": repo["updated_at"]
        }
        for repo in items
    ]

    return results

search_github_agent = create_react_agent(
    name="search_github_agent",
    model=model,
    tools=[get_repositories],
    prompt=search_github_agent_prompt
)





"""

class Repository(BaseModel):
    id: int = Field(description="The unique identifier of the repository.")
    name: str = Field(description="The name of the repository.")
    owner: str = Field(description="The owner of the repository.")
    description: str = Field(description="A brief description of the repository.")
    main_language: Optional[str] = Field(description="The primary programming language used in the repository.")
    url: str = Field(description="The URL of the repository.")
    stars: int = Field(description="The number of stars the repository has received.")
    created_at: str = Field(description="The date and time when the repository was created.")
    open_issues: int = Field(description="The number of open issues in the repository.")
    updated_at: str = Field(description="The date and time when the repository was last updated.")

class SearchGithubAgentState(TypeDict):
    project_description: str = Field(description="Project description provided by the user.")
    search_querie: str = Field(description="Search query generated based on the project description.")
    repos: List[Repository] = Field(description="List of repositories retrieved from GitHub based on the search queries.")


"""