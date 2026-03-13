"""
Skill Executor Tool - Dynamically loads and executes skills.

This module provides a LangChain tool that can dynamically import and execute
skills based on their name and input parameters.
"""

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Annotated, Any, Dict
from langchain_core.tools import tool
from core.skill_registry import get_registry
from core.exceptions import SkillNotFoundError, SkillExecutionError
from core.logger import setup_logger

logger = setup_logger("skill_executor")


def execute_skill(skill_name: str, **inputs) -> str:
    """
    Execute a skill by dynamically importing and running its tool.py module.
    
    Args:
        skill_name: Name of the skill to execute
        **inputs: Input parameters for the skill
    
    Returns:
        String result from the skill execution
    
    Raises:
        SkillNotFoundError: If skill doesn't exist in registry
        SkillExecutionError: If skill execution fails
    """
    logger.info(f"Executing skill: {skill_name} with inputs: {inputs}")
    
    # Get skill metadata from registry
    registry = get_registry()
    try:
        skill_metadata = registry.get_skill(skill_name)
    except SkillNotFoundError as e:
        logger.error(f"Skill not found: {skill_name}")
        return f"Error: {str(e)}"
    
    # Get the skill directory
    skill_dir = skill_metadata.get('skill_dir')
    if not skill_dir:
        error_msg = f"Skill '{skill_name}' has no skill_dir in metadata"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    
    # Path to tool.py
    tool_file = Path(skill_dir) / "tool.py"
    
    if not tool_file.exists():
        error_msg = f"Skill '{skill_name}' missing tool.py file at {tool_file}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    
    try:
        # Dynamic import of the tool module
        module_name = f"skills.{skill_name}.tool"
        
        # Check if module already imported
        if module_name in sys.modules:
            module = sys.modules[module_name]
            logger.debug(f"Reusing cached module: {module_name}")
        else:
            # Load module from file
            spec = importlib.util.spec_from_file_location(module_name, tool_file)
            if spec is None or spec.loader is None:
                raise SkillExecutionError(f"Could not load module spec for {tool_file}")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            logger.debug(f"Loaded module: {module_name}")
        
        # Check for run() function
        if not hasattr(module, 'run'):
            raise SkillExecutionError(
                f"Skill '{skill_name}' tool.py missing run() function"
            )
        
        # Execute the skill's run() function
        run_func = getattr(module, 'run')
        result = run_func(**inputs)
        
        logger.info(f"✓ Skill '{skill_name}' executed successfully")
        return str(result)
        
    except Exception as e:
        error_msg =f"Skill execution failed for '{skill_name}': {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


@tool
def execute_skill_tool(
    skill_name: Annotated[str, "Name of the skill to execute"],
    inputs: Annotated[str, "JSON string of input parameters (e.g., '{\"query\": \"search term\"}')"] = "{}"
) -> str:
    """
    Execute a dynamic skill from the skill registry.
    
    Use this tool to execute any registered skill based on the user's request.
    Check the available skills in the system prompt to see what's available.
    
    Args:
        skill_name: The name of the skill to execute
        inputs: JSON string containing the input parameters for the skill
    
    Returns:
        Result from the skill execution as a string
    """
    import json
    
    logger.debug(f"execute_skill_tool called: skill_name={skill_name}, inputs={inputs}")
    
    # Parse inputs JSON
    try:
        if isinstance(inputs, str):
            input_dict = json.loads(inputs) if inputs.strip() else {}
        elif isinstance(inputs, dict):
            input_dict = inputs
        else:
            input_dict = {}
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON in inputs parameter: {e}"
    
    # Execute the skill
    return execute_skill(skill_name, **input_dict)


# Simpler alternative tool with direct parameters
def create_skill_tool_simple():
    """
    Create a simpler version of the skill executor that takes direct parameters.
    
    This version extracts the first input parameter from the skill and uses it directly.
    Better for simple skills with single inputs.
    """
    @tool
    def execute_skill_simple(
        skill_name: Annotated[str, "Name of the skill to execute"],
        query: Annotated[str, "Input query or parameter for the skill"] = ""
    ) -> str:
        """
        Execute a skill with a simple query parameter.
        
        Most skills accept a 'query' parameter. Use this for quick skill execution.
        For skills with multiple parameters, use execute_skill_tool instead.
        """
        import re

        # Auto-correct: detect a .pdf file path anywhere in the query
        pdf_match = re.search(r'[A-Za-z:\\/.][^\s]*\.pdf', query, re.IGNORECASE)
        if pdf_match and skill_name != 'pdf_extractor':
            logger.info(f"PDF path detected — auto-routing from '{skill_name}' to 'pdf_extractor'")
            skill_name = 'pdf_extractor'
            query = pdf_match.group(0)  # pass only the clean file path

        registry = get_registry()
        try:
            skill_metadata = registry.get_skill(skill_name)

            # Map query to the skill's first input parameter name
            inputs_def = skill_metadata.get('inputs', {})
            if inputs_def:
                first_param = list(inputs_def.keys())[0]
                input_dict = {first_param: query}
            else:
                input_dict = {'query': query}

            return execute_skill(skill_name, **input_dict)

        except SkillNotFoundError as e:
            return f"Error: {str(e)}"
    
    return execute_skill_simple
