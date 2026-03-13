"""
Dynamic Skill-Based AI Agent

Main interface for the skill-based agent system.

Example Usage:
    Basic usage:
        >>> from agent import SkillAgent
        >>> agent = SkillAgent()
        >>> result = agent.invoke("Calculate 25 * 37")
        >>> print(result)
    
    With streaming:
        >>> for chunk in agent.stream("Search for Python tutorials"):
        ...     print(chunk, end="", flush=True)
    
    Custom model:
        >>> agent = SkillAgent(model_name="llama3-70b-8192")
        >>> result = agent.invoke("What is 2+2?")
"""

import sys
from pathlib import Path
from typing import Dict, Any, Generator, Optional
import os

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.agent_factory import create_skill_agent
from core.skill_registry import get_registry
from core.logger import setup_logger

logger = setup_logger(__name__)


class SkillAgent:
    """
    Main interface for the dynamic skill-based AI agent.
    
    This agent can dynamically load and execute skills defined in skills.md files.
    Each skill is a separate module with metadata and implementation.
    
    Attributes:
        agent: The underlying LangChain agent
        skills_dir: Directory containing skill modules
        model_name: Name of the LLM model to use
    """
    
    def __init__(self, skills_dir: str = "skills", model_name: Optional[str] = None):
        """
        Initialize the skill agent.
        
        Args:
            skills_dir: Path to skills directory (default: "skills")
            model_name: Groq model name (default: from GROQ_MODEL env or "llama-3.3-70b-versatile")
        """
        self.skills_dir = skills_dir
        # Get model name from parameter, environment, or default
        if model_name is None:
            model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.model_name = model_name
        
        logger.info(f"Initializing SkillAgent with model: {model_name}")
        
        # Create the agent
        self.agent = create_skill_agent(
            skills_dir=skills_dir,
            model_name=model_name
        )
        
        # Get skill count
        registry = get_registry()
        skill_names = registry.get_skill_names()
        
        logger.info(f"Agent initialized with {len(skill_names)} skills: {skill_names}")
    
    def invoke(self, query: str) -> str:
        """
        Run the agent on a query and get the final response.
        
        Args:
            query: User query/question
        
        Returns:
            Agent's response as a string
        """
        logger.info(f"Invoking agent with query: {query}")
        
        try:
            # Use agent executor's invoke method
            messages = [{"role": "user", "content": query}]
            result = self.agent.invoke({"messages": messages})
            
            # Extract the final response
            if "messages" in result and result["messages"]:
                final_message = result["messages"][-1]
                response = final_message.content if hasattr(final_message, 'content') else str(final_message)
            else:
                response = str(result)
            
            logger.info("Agent completed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error during agent invocation: {e}", exc_info=True)
            return f"Error: {str(e)}"
    
    def stream(self, query: str) -> Generator[str, None, None]:
        """
        Stream the agent's response, yielding (node_name, content) tuples.
        node_name is 'agent', 'tools', or 'final'.
        
        Args:
            query: User query/question
        
        Yields:
            Tuples of (node_name: str, content: str)
        """
        logger.info(f"Streaming agent response for query: {query}")
        
        try:
            messages = [{"role": "user", "content": query}]
            
            for chunk in self.agent.stream({"messages": messages}):
                # LangGraph chunks: {"agent": {"messages": [...]}, "tools": {"messages": [...]}}
                for node_name, node_data in chunk.items():
                    if not isinstance(node_data, dict):
                        continue
                    for message in node_data.get("messages", []):
                        content = getattr(message, "content", "") or ""
                        tool_calls = getattr(message, "tool_calls", [])
                        msg_type = type(message).__name__
                        if content and not tool_calls and msg_type == "AIMessage":
                            yield ("final", content)
                        elif tool_calls and msg_type == "AIMessage":
                            for tc in tool_calls:
                                yield ("tools", tc.get("name", "unknown"))
                        elif msg_type == "ToolMessage" and content:
                            yield ("tool_result", content)
                    
        except Exception as e:
            logger.error(f"Error during streaming: {e}", exc_info=True)
            yield ("error", str(e))
    
    def list_skills(self) -> Dict[str, Any]:
        """
        Get information about all loaded skills.
        
        Returns:
            Dictionary mapping skill names to their metadata
        """
        registry = get_registry()
        return registry.list_all_skills()
    
    def get_skill_info(self, skill_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific skill.
        
        Args:
            skill_name: Name of the skill
        
        Returns:
            Skill metadata dictionary
        """
        registry = get_registry()
        try:
            return registry.get_skill(skill_name)
        except Exception as e:
            logger.error(f"Error getting skill info: {e}")
            return {}


def main():
    """
    Interactive CLI for the skill agent.
    """
    print("=" * 60)
    print("Dynamic Skill-Based AI Agent")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        print("\n⚠️  ERROR: GROQ_API_KEY not found in environment!")
        print("Please set it in your .env file or environment variables.")
        return
    
    # Initialize agent
    print("\nInitializing agent...")
    agent = SkillAgent()
    
    # Show loaded skills
    print(f"\n✓ Agent ready!")
    skills = agent.list_skills()
    print(f"\nLoaded {len(skills)} skills:")
    for skill_name, metadata in skills.items():
        print(f"  • {skill_name}: {metadata.get('description', 'No description')}")
    
    # Interactive loop
    print("\n" + "=" * 60)
    print("Enter your queries (or 'quit' to exit)")
    print("=" * 60 + "\n")
    
    while True:
        try:
            query = input("\n🤔 You: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye! 👋")
                break
            
            if query.lower() == 'skills':
                print("\nAvailable skills:")
                for skill_name, metadata in agent.list_skills().items():
                    print(f"\n  {skill_name}:")
                    print(f"    Description: {metadata.get('description', 'N/A')}")
                    print(f"    Inputs: {metadata.get('inputs', {})}")
                continue
            
            print("\n🤖 Agent: ", end="", flush=True)
            
            got_response = False
            for node, content in agent.stream(query):
                if node == "tools":
                    print(f"\n  ⚙ Using skill: {content}", flush=True)
                    print("🤖 Agent: ", end="", flush=True)
                elif node == "final":
                    print(content, flush=True)
                    got_response = True
                elif node == "error":
                    print(f"\n❌ Stream error: {content}", flush=True)
                    got_response = True
            
            # Fallback: if stream yielded nothing, use invoke
            if not got_response:
                result = agent.invoke(query)
                print(result, flush=True)
            else:
                print()  # trailing newline
            
        except KeyboardInterrupt:
            print("\n\nKeyboard interrupt detected. Goodbye! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.error(f"Error in main loop: {e}", exc_info=True)


if __name__ == "__main__":
    main()
