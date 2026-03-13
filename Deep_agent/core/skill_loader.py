"""
Skill Loader - Scans and parses skills.md metadata files.

This module discovers skills from the skills/ directory and parses their
YAML metadata into structured skill definitions.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from core.exceptions import SkillLoadError, SkillValidationError
from core.logger import setup_logger

logger = setup_logger("skill_loader")


def scan_skills_directory(skills_dir: str = "skills") -> List[Path]:
    """
    Recursively scan the skills directory for skills.md files.
    
    Args:
        skills_dir: Path to the skills directory (default: "skills")
    
    Returns:
        List of Path objects pointing to skills.md files
    
    Raises:
        SkillLoadError: If skills directory doesn't exist
    """
    skills_path = Path(skills_dir)
    
    if not skills_path.exists():
        logger.warning(f"Skills directory not found: {skills_dir}")
        return []
    
    if not skills_path.is_dir():
        raise SkillLoadError(f"Skills path is not a directory: {skills_dir}")
    
    # Find all skills.md files recursively
    skill_files = list(skills_path.rglob("skills.md"))
    
    logger.info(f"Found {len(skill_files)} skill files in {skills_dir}")
    
    return skill_files


def parse_skill_metadata(skill_file: Path) -> Dict[str, Any]:
    """
    Parse a skills.md file and extract YAML metadata.
    
    Expected format:
    ```yaml
    name: skill_name
    description: What the skill does
    inputs:
      param1: type
      param2: type
    outputs:
      - output_name
    use_when:
      - Condition 1
      - Condition 2
    ```
    
    Args:
        skill_file: Path to the skills.md file
    
    Returns:
        Dictionary containing skill metadata
    
    Raises:
        SkillLoadError: If file cannot be read or parsed
        SkillValidationError: If required fields are missing
    """
    try:
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse YAML content (entire file is YAML for now)
        metadata = yaml.safe_load(content)
        
        if not isinstance(metadata, dict):
            raise SkillValidationError(f"Invalid YAML in {skill_file}: expected dictionary")
        
        # Validate required fields
        required_fields = ['name', 'description', 'inputs']
        missing_fields = [field for field in required_fields if field not in metadata]
        
        if missing_fields:
            raise SkillValidationError(
                f"Missing required fields in {skill_file}: {', '.join(missing_fields)}"
            )
        
        # Add skill directory path for tool.py location
        metadata['skill_dir'] = skill_file.parent
        metadata['skill_file'] = str(skill_file)
        
        logger.debug(f"Parsed skill: {metadata['name']}")
        
        return metadata
        
    except yaml.YAMLError as e:
        raise SkillLoadError(f"YAML parsing error in {skill_file}: {e}")
    except Exception as e:
        raise SkillLoadError(f"Error reading {skill_file}: {e}")


def load_all_skills(skills_dir: str = "skills") -> List[Dict[str, Any]]:
    """
    Load and parse all skills from the skills directory.
    
    Args:
        skills_dir: Path to the skills directory
    
    Returns:
        List of skill metadata dictionaries
    """
    skill_files = scan_skills_directory(skills_dir)
    skills = []
    errors = []
    
    for skill_file in skill_files:
        try:
            metadata = parse_skill_metadata(skill_file)
            skills.append(metadata)
            logger.info(f"✓ Loaded skill: {metadata['name']}")
        except (SkillLoadError, SkillValidationError) as e:
            logger.error(f"✗ Failed to load {skill_file}: {e}")
            errors.append(str(e))
    
    if skills:
        logger.info(f"Successfully loaded {len(skills)} skill(s)")
    
    if errors:
        logger.warning(f"Failed to load {len(errors)} skill(s)")
    
    return skills
