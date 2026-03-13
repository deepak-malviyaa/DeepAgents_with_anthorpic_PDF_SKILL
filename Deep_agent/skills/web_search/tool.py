"""
Web Search Skill

Searches for information, prints results to the screen, and saves them to a file.
Replace the mock implementation with a real search API (Tavily, Google, etc.)
"""

import os
from datetime import datetime
from pathlib import Path


RESULTS_DIR = Path("search_results")


def run(query: str) -> str:
    """
    Search the web for information, print to screen, and save to a file.

    Args:
        query: Search query string

    Returns:
        Search results string (also saved to file)
    """
    # --- Build results ---
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results = f"""Web Search Results
{'=' * 50}
Query   : {query}
Time    : {timestamp}
{'=' * 50}

🔍 Result 1:
  Title   : Introduction to {query}
  URL     : https://example.com/intro
  Summary : This is a comprehensive guide about {query}.

🔍 Result 2:
  Title   : {query} - Best Practices
  URL     : https://example.com/best-practices
  Summary : Learn the best practices for working with {query}.

🔍 Result 3:
  Title   : Latest Updates on {query}
  URL     : https://example.com/updates
  Summary : Recent developments and news about {query}.

{'=' * 50}
Note: Mock results. Set TAVILY_API_KEY in .env for real search.
"""

    # --- Print to screen ---
    print(results)

    # --- Save to file ---
    RESULTS_DIR.mkdir(exist_ok=True)
    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in query[:50]).strip()
    filename = RESULTS_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_name}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(results)

    print(f"\n💾 Results saved to: {filename}")

    return results + f"\n\n💾 Saved to: {filename}"
