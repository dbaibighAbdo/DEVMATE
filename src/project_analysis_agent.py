from langgraph.graph import MessagesState, StateGraph, START, END
from pydantic import BaseModel, Field
from typing import List, Optional


class ProjectAnalysisAgentState(MessagesState):
    """"State for the project analysis agent workflow."""





def download_best_repo(state):
    """
    Function to download the repository.
    """
    pass


def analyze_project(state):
    """
    Function to analyze repository.
    """
    pass
