"""
Skill Registry - Stores and retrieves skill metadata.

Provides a centralized registry for managing loaded skills and formatting
them for LLM consumption.
"""

from typing import Dict, List, Any, Optional
from threading import Lock
from core.exceptions import SkillNotFoundError
from core.logger import setup_logger
from core.skill_loader import load_all_skills

logger = setup_logger("skill_registry")


class SkillRegistry:
    """
    Thread-safe singleton registry for skill metadata.
    
    Stores skill definitions and provides methods to retrieve and format
    them for agent prompts.
    """
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the registry (only once)."""
        if self._initialized:
            return
        
        self._skills: Dict[str, Dict[str, Any]] = {}
        self._initialized = True
        logger.debug("SkillRegistry initialized")
    
    def register(self, skill_metadata: Dict[str, Any]) -> None:
        """
        Register a skill in the registry.
        
        Args:
            skill_metadata: Dictionary containing skill metadata
        
        Raises:
            ValueError: If skill_metadata is invalid or missing 'name'
        """
        if not isinstance(skill_metadata, dict):
            raise ValueError("skill_metadata must be a dictionary")
        
        if 'name' not in skill_metadata:
            raise ValueError("skill_metadata must contain 'name' field")
        
        skill_name = skill_metadata['name']
        
        with self._lock:
            self._skills[skill_name] = skill_metadata
        
        logger.debug(f"Registered skill: {skill_name}")
    
    def get_skill(self, skill_name: str) -> Dict[str, Any]:
        """
        Retrieve skill metadata by name.
        
        Args:
            skill_name: Name of the skill to retrieve
        
        Returns:
            Dictionary containing skill metadata
        
        Raises:
            SkillNotFoundError: If skill doesn't exist in registry
        """
        with self._lock:
            if skill_name not in self._skills:
                available = ', '.join(self._skills.keys()) if self._skills else 'none'
                raise SkillNotFoundError(
                    f"Skill '{skill_name}' not found. Available skills: {available}"
                )
            return self._skills[skill_name].copy()
    
    def list_all_skills(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered skills as a dict keyed by skill name.
        
        Returns:
            Dict mapping skill name to skill metadata
        """
        with self._lock:
            return {name: skill.copy() for name, skill in self._skills.items()}
    
    def get_skill_names(self) -> List[str]:
        """
        Get list of all registered skill names.
        
        Returns:
            List of skill names
        """
        with self._lock:
            return list(self._skills.keys())
    
    def get_skills_for_prompt(self) -> str:
        """
        Format skills for inclusion in the system prompt.
        
        Returns formatted string with skill descriptions that the LLM can
        use to decide which skill to execute.
        
        Returns:
            Formatted string describing all available skills
        """
        with self._lock:
            if not self._skills:
                return "No skills available."
            
            prompt_parts = ["Available Skills:\n"]
            
            for skill_name, metadata in self._skills.items():
                prompt_parts.append(f"\n**{skill_name}**")
                prompt_parts.append(f"- Description: {metadata.get('description', 'N/A')}")
                
                # Format inputs
                inputs = metadata.get('inputs', {})
                if inputs:
                    input_strs = [f"{k}: {v}" for k, v in inputs.items()]
                    prompt_parts.append(f"- Inputs: {', '.join(input_strs)}")
                
                # Format use_when
                use_when = metadata.get('use_when', [])
                if use_when:
                    if isinstance(use_when, list):
                        prompt_parts.append("- Use when:")
                        for condition in use_when:
                            prompt_parts.append(f"  • {condition}")
                    else:
                        prompt_parts.append(f"- Use when: {use_when}")
            
            return "\n".join(prompt_parts)
    
    def initialize(self, skills_dir: str = "skills") -> int:
        """
        Initialize the registry by loading all skills from directory.
        
        Args:
            skills_dir: Path to skills directory
        
        Returns:
            Number of skills loaded
        """
        logger.info(f"Initializing skill registry from: {skills_dir}")
        
        skills = load_all_skills(skills_dir)
        
        for skill_metadata in skills:
            self.register(skill_metadata)
        
        logger.info(f"Registry initialized with {len(skills)} skill(s)")
        
        return len(skills)
    
    def clear(self) -> None:
        """Clear all registered skills (useful for testing)."""
        with self._lock:
            self._skills.clear()
        logger.debug("Registry cleared")
    
    def __repr__(self) -> str:
        """String representation of registry."""
        count = len(self._skills)
        names = ', '.join(self._skills.keys()) if self._skills else 'none'
        return f"SkillRegistry(skills={count}, names=[{names}])"


# Convenience function to get the singleton instance
def get_registry() -> SkillRegistry:
    """Get the global SkillRegistry instance."""
    return SkillRegistry()
