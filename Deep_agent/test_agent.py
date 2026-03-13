"""
Test script for the dynamic skill agent system.

Run this to verify all components work correctly.
"""

import sys
from pathlib import Path
import os

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agent import SkillAgent
from core.skill_registry import get_registry
from core.logger import setup_logger

logger = setup_logger(__name__)


def test_skill_loading():
    """Test that skills are loaded correctly."""
    print("\n" + "=" * 60)
    print("TEST 1: Skill Loading")
    print("=" * 60)
    
    registry = get_registry()
    registry.clear()  # Clear any existing skills
    
    skills_count = registry.initialize("skills")
    print(f"✓ Loaded {skills_count} skills")
    
    skills = registry.list_all_skills()
    print(f"\nLoaded skills:")
    for name, metadata in skills.items():
        print(f"  • {name}")
        print(f"    Description: {metadata.get('description', 'N/A')}")
        print(f"    Inputs: {metadata.get('inputs', {})}")
        print(f"    Use when: {metadata.get('use_when', [])[:2]}...")  # First 2 items
    
    return skills_count > 0


def test_skill_execution():
    """Test executing skills directly."""
    print("\n" + "=" * 60)
    print("TEST 2: Direct Skill Execution")
    print("=" * 60)
    
    from tools.skill_tool import execute_skill
    
    # Test calculator skill
    print("\nTesting calculator skill...")
    try:
        result = execute_skill("calculator", expression="25 * 37")
        print(f"✓ Calculator result:\n{result}")
    except Exception as e:
        print(f"✗ Calculator failed: {e}")
        return False
    
    # Test web_search skill
    print("\nTesting web_search skill...")
    try:
        result = execute_skill("web_search", query="Python tutorials")
        print(f"✓ Web search result:\n{result[:200]}...")  # First 200 chars
    except Exception as e:
        print(f"✗ Web search failed: {e}")
        return False
    
    return True


def test_agent_basic():
    """Test basic agent functionality."""
    print("\n" + "=" * 60)
    print("TEST 3: Basic Agent Invocation")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        print("✗ GROQ_API_KEY not found in environment")
        print("  Set it in .env file or environment variables")
        return False
    
    print("\nInitializing agent...")
    try:
        agent = SkillAgent()
        print("✓ Agent initialized")
    except Exception as e:
        print(f"✗ Agent initialization failed: {e}")
        logger.error("Agent init failed", exc_info=True)
        return False
    
    # Test calculation
    print("\nTest query: 'What is 123 * 456?'")
    try:
        result = agent.invoke("What is 123 * 456?")
        print(f"✓ Response:\n{result}")
    except Exception as e:
        print(f"✗ Agent invocation failed: {e}")
        logger.error("Agent invocation failed", exc_info=True)
        return False
    
    return True


def test_agent_skills():
    """Test agent using different skills."""
    print("\n" + "=" * 60)
    print("TEST 4: Agent Skill Selection")
    print("=" * 60)
    
    if not os.getenv("GROQ_API_KEY"):
        print("✗ Skipping (no API key)")
        return False
    
    agent = SkillAgent()
    
    test_queries = [
        "Calculate 15 + 27",
        "Search for machine learning courses",
        "Summarize this text: Artificial intelligence is transforming the world. Machine learning enables computers to learn from data. Deep learning uses neural networks.",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nQuery {i}: {query}")
        try:
            result = agent.invoke(query)
            print(f"✓ Response:\n{result[:300]}...")  # First 300 chars
        except Exception as e:
            print(f"✗ Failed: {e}")
            return False
    
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("SKILL AGENT SYSTEM TESTS")
    print("=" * 60)
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    results = {}
    
    # Test 1: Skill loading
    try:
        results['skill_loading'] = test_skill_loading()
    except Exception as e:
        print(f"✗ Skill loading test crashed: {e}")
        results['skill_loading'] = False
    
    # Test 2: Direct execution
    try:
        results['skill_execution'] = test_skill_execution()
    except Exception as e:
        print(f"✗ Skill execution test crashed: {e}")
        results['skill_execution'] = False
    
    # Test 3: Basic agent
    try:
        results['agent_basic'] = test_agent_basic()
    except Exception as e:
        print(f"✗ Basic agent test crashed: {e}")
        results['agent_basic'] = False
    
    # Test 4: Agent skills (optional if API key available)
    try:
        if os.getenv("GROQ_API_KEY"):
            results['agent_skills'] = test_agent_skills()
        else:
            results['agent_skills'] = None  # Skipped
    except Exception as e:
        print(f"✗ Agent skills test crashed: {e}")
        results['agent_skills'] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        if result is None:
            status = "⊘ SKIPPED"
        elif result:
            status = "✓ PASSED"
        else:
            status = "✗ FAILED"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    
    print(f"\nResults: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed == 0 and passed > 0:
        print("\n🎉 All tests passed!")
        return True
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
