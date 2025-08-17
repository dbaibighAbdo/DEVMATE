from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import httpx
import os
import zipfile

load_dotenv()

model = ChatOpenAI(model="gpt-4o")


project_assistant_agent_prompt = """
You are the `project_assistant_agent`. Your role is to help the SUPERVISOR with coding, analyzing repositories, and building projects.

You will receive two types of requests from the SUPERVISOR:
    1. A repository URL to download and analyze.
    2. A request to debug or optimize code (may or may not be part of a repository).

---

### 1. When you receive a repository URL:
    - Tasks:
        Decide which tool(s) to use and in what order.
        You may choose to:
        Download the repository (using {download_zipped_repo}) if you need access to its code.
        Unzip the repository (using {unzip_repo}) if you need to explore its contents.
        List files (using {list_files}) if you want to understand the structure.
        Read a file (using {read_file}) if you need details about specific components.
        Use the tools only when necessary, and combine reasoning with tool outputs.
        Provide clear insights, summaries, and actionable suggestions about the project once you have enough information.

---

### 2. When you receive a debug or optimization request (with or without a repository):
    - Tasks:
        1. Identify issues in the provided code.
        2. Suggest optimizations or fixes.
        3. Provide clear, step-by-step instructions for implementing the changes.

---

### GENERAL GUIDELINES:
- Always clarify unclear or incomplete requests before acting.
- Think step-by-step before providing a response.
- Use Markdown for all outputs.
- Do not invent information — base answers only on available data.
- Keep tone friendly and concise.
- Present analysis or instructions in a clear, structured format (headings, bullet points, code blocks as needed).

---
### Example Output Format (Code Help / Repository Analysis):

**Repository Name**: <name> (if applicable)  
**Main Language**: <language>  
**Description**: <short summary> (if applicable)

**Key Directories & Files**: (if repository provided)  
- /src — core logic  
- /tests — unit tests  

**Dependencies**: (if repository provided)  
- <package> — purpose  

**Suggested Next Steps / Fixes**:  
1. <step>  
2. <step>  
3. <step>
"""



@tool
def download_zipped_repo(repo_url: str, branch: str = "main", save_path: str = "./repo.zip") -> str:
    """
    Downloads a GitHub repository as a .zip file.

    Args:
        repo_url (str): GitHub repo URL (e.g., https://github.com/tiangolo/fastapi).
        branch (str): Branch to download (default: main).
        save_path (str): Where to save the zip file.

    Returns:
        str: Path to the saved zip file.
    """
    parts = repo_url.rstrip("/").split("/")
    if len(parts) < 2:
        raise ValueError("Invalid GitHub URL. Expected format: https://github.com/owner/repo")

    owner, repo = parts[-2], parts[-1]
    zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"

    with httpx.Client() as client:
        response = client.get(zip_url)
        if response.status_code != 200:
            raise Exception(f"Failed to download repo: {response.status_code}, {response.text}")

        with open(save_path, "wb") as f:
            f.write(response.content)

    return os.path.abspath(save_path)


# 2️⃣ Unzip repo
@tool
def unzip_repo(zip_path: str, extract_to: str = "./repo") -> str:
    """
    Extracts a .zip file into a folder.

    Args:
        zip_path (str): Path to the .zip file.
        extract_to (str): Destination directory.

    Returns:
        str: Path to extracted folder.
    """
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)

    # Most GitHub archives create a subfolder repo-branch/
    extracted_dir = os.path.join(extract_to, os.listdir(extract_to)[0])
    return os.path.abspath(extracted_dir)


# 3️⃣ List files in repo
@tool
def list_files(folder_path: str, max_files: int = 50) -> str:
    """
    Lists files in a repo folder.

    Args:
        folder_path (str): Path to the repo folder.
        max_files (int): Max number of files to list (default: 50).

    Returns:
        str: Text listing of files (for LLM consumption).
    """
    file_list = []
    for root, dirs, files in os.walk(folder_path):
        for f in files:
            rel_path = os.path.relpath(os.path.join(root, f), folder_path)
            file_list.append(rel_path)

            if len(file_list) >= max_files:
                return "\n".join(file_list)

    return "\n".join(file_list) if file_list else "No files found."


# 4️⃣ Read file content
@tool
def read_file(file_path: str, max_chars: int = 5000) -> str:
    """
    Reads the content of a file.

    Args:
        file_path (str): Path to the file.
        max_chars (int): Limit characters returned (default: 5000).

    Returns:
        str: File content (truncated if too long).
    """
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    if len(content) > max_chars:
        return content[:max_chars] + "\n... [truncated]"
    return content



project_assistant_agent = create_react_agent(
    name="project_assistant_agent",
    model=model,
    tools=[download_zipped_repo, unzip_repo, list_files, read_file],
    prompt=project_assistant_agent_prompt,
)
