"""
Agent Factory - Creates skill-powered vanilla agents.

This module provides factory functions to create LangChain agents
configured with dynamic skill loading capabilities.
"""

import os
from typing import List, Optional
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.tools import BaseTool
from core.skill_registry import get_registry
from core.logger import setup_logger
from tools.skill_tool import execute_skill_tool, create_skill_tool_simple

logger = setup_logger("agent_factory")

# Load environment variables
load_dotenv()


def create_skill_agent(
    skills_dir: str = "skills",
    model_name: Optional[str] = None,
    additional_tools: Optional[List[BaseTool]] = None,
    use_simple_skill_tool: bool = True,
    temperature: float = 0.7
):
    """
    Create a vanilla agent with dynamic skill loading.
    
    This function:
    1. Initializes the skill registry from skills directory
    2. Creates a Groq LLM
    3. Builds a system prompt with skill descriptions
    4. Includes the skill executor tool
    5. Returns a configured agent
    
    Args:
        skills_dir: Directory containing skill definitions (default: "skills")
        model_name: Groq model to use (default: "llama3-8b-8192")
        additional_tools: Extra tools to include beyond skill executor
        use_simple_skill_tool: Use simple skill tool vs JSON-based (default: True)
        temperature: LLM temperature (default: 0.7)
    
    Returns:
        Configured LangChain agent ready to invoke
    
    Raises:
        ValueError: If GROQ_API_KEY not found in environment
    """
    logger.info("Creating skill-powered agent")
    
    # Get API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    
    # Get model name from environment or use parameter or default
    if model_name is None:
        model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    # Initialize skill registry
    logger.info(f"Loading skills from: {skills_dir}")
    registry = get_registry()
    skill_count = registry.initialize(skills_dir)
    
    if skill_count == 0:
        logger.warning(f"No skills found in {skills_dir}")
    
    # Initialize Groq model
    logger.info(f"Initializing model: {model_name}")
    model = ChatGroq(
        model=model_name,
        api_key=api_key,
        temperature=temperature
    )
    
    # Build tools list
    tools = []
    
    # Add skill executor tool
    if use_simple_skill_tool:
        skill_tool = create_skill_tool_simple()
        logger.debug("Using simple skill tool")
    else:
        skill_tool = execute_skill_tool
        logger.debug("Using JSON-based skill tools")
    
    tools.append(skill_tool)
    
    # Add any additional tools
    if additional_tools:
        tools.extend(additional_tools)
        logger.debug(f"Added {len(additional_tools)} additional tools")
    
    # Build system prompt with skill catalog
    skill_catalog = registry.get_skills_for_prompt()
    skill_names = registry.get_skill_names()
    
    system_prompt = f"""You are a helpful AI assistant.

You have ONE tool available: execute_skill_simple
You MUST ONLY call the tool named `execute_skill_simple`. Never call any other tool name.

To run a skill, call execute_skill_simple like this:
  skill_name = "<one of: {', '.join(skill_names)}>"
  query = "<the user's input>"

## HARD RULES (always apply, override everything else)
1. If the user's message contains a file path ending in .pdf — use skill_name="pdf_extractor" and set query to that file path. No exceptions.
2. NEVER use text_summarizer or web_search for a PDF file path.
3. ALWAYS use execute_skill_simple. Never call a skill name directly as a tool.

## Available Skills
{skill_catalog}

- Pick the skill whose use_when conditions best match the user's request.
- If no skill matches, answer from your own knowledge without calling any tool."""
    
    # Create vanilla agent
    logger.info("Creating agent with vanilla LangChain")
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt
    )
    
    logger.info(f"✓ Agent created with {len(tools)} tool(s) and {skill_count} skill(s)")
    logger.info(f"✓ Skills: {', '.join(registry.get_skill_names()) if skill_count > 0 else 'none'}")
    
    return agent


def create_minimal_agent(
    model_name: Optional[str] = None,
    tools: Optional[List[BaseTool]] = None,
    system_prompt: str = "You are a helpful assistant.",
    temperature: float = 0.7
):
    """
    Create a minimal vanilla agent without skills.
    
    This is the absolute minimal agent for comparison/testing.
    
    Args:
        model_name: Groq model to use
        tools: List of tools to include
        system_prompt: Custom system prompt
        temperature: LLM temperature
    
    Returns:
        Configured LangChain agent
    
    Raises:
        ValueError: If GROQ_API_KEY not found
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    
    # Get model name from environment or use parameter or default
    if model_name is None:
        model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    model = ChatGroq(
        model=model_name,
        api_key=api_key,
        temperature=temperature
    )
    
    agent = create_agent(
        model=model,
        tools=tools or [],
        system_prompt=system_prompt
    )
    
    logger.info(f"Created minimal agent with {len(tools or [])} tool(s)")
    
    return agent
