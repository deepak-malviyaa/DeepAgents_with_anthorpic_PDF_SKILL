# Dynamic Skill-Based AI Agent

A modular AI agent system where skills are defined as self-contained modules with YAML metadata and Python implementations. The agent dynamically discovers, loads, and selects the right skill at runtime — no code changes needed to add new capabilities.

---

## Quick Start

### 1. Setup

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1  # PowerShell

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure `.env`

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

Get your API key at: https://console.groq.com/

### 3. Run the Agent

```bash
# Interactive CLI
python agent.py

# Run tests
python test_agent.py
```

---

## Project Structure

```
Deep_agent/
├── agent.py              # Main entry point — SkillAgent class + CLI
├── test_agent.py         # Test suite
├── requirements.txt      # Dependencies
├── .env                  # API keys and model config (not in git)
├── .gitignore
│
├── core/                 # Core infrastructure
│   ├── agent_factory.py  # Creates skill-aware LangChain agents
│   ├── skill_loader.py   # Scans and parses skills.md files
│   ├── skill_registry.py # Thread-safe singleton skill store
│   ├── exceptions.py     # Custom exception classes
│   ├── logger.py         # Logging setup
│   └── __init__.py
│
├── tools/                # LangChain tool wrappers
│   ├── skill_tool.py     # Dynamic skill executor (importlib-based)
│   └── __init__.py
│
└── skills/               # Skill definitions (add new folders here)
    ├── calculator/
    │   ├── skills.md     # YAML metadata
    │   └── tool.py       # run() implementation
    ├── web_search/
    │   ├── skills.md
    │   └── tool.py
    └── text_summarizer/
        ├── skills.md
        └── tool.py
```

---

## How Skills Work

Each skill lives in its own folder under `skills/` with two files:

**`skills.md`** — Metadata that tells the LLM when to use this skill:
```yaml
name: calculator
description: Perform mathematical calculations and solve expressions
inputs:
  expression: string
outputs:
  - result
use_when:
  - User asks to calculate a math expression
  - User wants to perform arithmetic operations
```

**`tool.py`** — The implementation with a `run()` function:
```python
def run(expression: str) -> str:
    result = eval(expression, {"__builtins__": {}}, {"pow": pow, "abs": abs})
    return f"Result: {result}"
```

The agent reads all `skills.md` files on startup, builds a skill catalog in the system prompt, and uses the `execute_skill` tool to call the right `tool.py` at runtime.

---

## Adding a New Skill

1. Create a folder: `skills/my_skill/`
2. Add `skills.md` with name, description, inputs, use_when
3. Add `tool.py` with a `run(**inputs)` function

No other changes needed. The agent picks it up automatically on next run.

---

## Usage in Code

```python
from agent import SkillAgent

agent = SkillAgent()                          # uses GROQ_MODEL from .env
result = agent.invoke("What is 144 / 12?")
print(result)

# Override model
agent = SkillAgent(model_name="llama3-8b-8192")

# List loaded skills
print(agent.list_skills())
```

---

## Model Configuration

Defined in `.env`, applied to all agents automatically:

```env
GROQ_MODEL=llama-3.3-70b-versatile
```

| Model | Parameters | Context | TPM | Best For |
|-------|-----------|---------|-----|----------|
| `llama-3.3-70b-versatile` | 70B | 32k | 6,000 | Production — best quality |
| `llama3-8b-8192` | 8B | 8k | 30,000 | Development — fastest |
| `llama-3.1-8b-instant` | 8B | 8k | 6,000 | Quick testing |

If you hit rate limits (413 error), switch to `llama3-8b-8192` which has 30k TPM.

---

## Resources

- [Groq Console](https://console.groq.com/)
- [LangChain Docs](https://python.langchain.com/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)


## 🚀 Quick Start

### 1. Setup Environment

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1  # PowerShell
# or
.\venv\Scripts\activate.bat  # CMD

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```
GROQ_API_KEY=your_actual_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

Get your Groq API key from: https://console.groq.com/

**Model Configuration:**
- Default model: `llama-3.3-70b-versatile` (70B, high quality, 32k context)
- For faster responses: Change to `llama3-8b-8192` (8B, fast, 30k TPM)
- For quick tests: Use `llama-3.1-8b-instant` (ultra-fast)

See [MODEL_CONFIG.md](MODEL_CONFIG.md) for all available models and configuration options.

### 3. Choose Your Agent

**Option A: Vanilla Agent (Recommended for token limits)**
```bash
python vanilla_agent.py
```
- Minimal token usage (~500-1,500 tokens)
- Only includes tools you define
- Perfect for Groq free tier
- Fast and lightweight

**Option B: Full DeepAgent**
```bash
python basic_agent.py
```
- Full features (~15,000 tokens)
- File operations, planning, context management
- Requires model with higher TPM limit

## 📁 Project Structure

```
Deep_agent/
├── vanilla_agent.py        # ⭐ Minimal agent (~500-1.5k tokens)
├── basic_agent.py          # Full DeepAgent (~15k tokens)
├── AGENT_COMPARISON.md     # Detailed comparison
├── requirements.txt        # Python dependencies
├── .env                    # API keys (not in git)
├── .env.example           # Template for .env
├── .gitignore             # Git ignore rules
└── README.md              # This file

Coming soon:
├── core/                  # Core skill system
│   ├── skill_loader.py   # Scans and loads skills
│   ├── skill_registry.py # Stores skill metadata
│   └── agent_factory.py  # Creates skill-aware agent
├── tools/                 # Custom LangChain tools
│   └── skill_tool.py     # Dynamic skill executor
├── skills/                # Skill definitions
│   ├── web_search/
│   │   ├── skills.md     # Skill metadata (YAML)
│   │   └── tool.py       # Skill implementation
│   └── calculator/
│       ├── skills.md
│       └── tool.py
├── api/                   # FastAPI server
│   └── server.py
└── agent.py              # Main skill agent interface
```

## 🎯 What is DeepAgent?

DeepAgent is an opinionated, ready-to-run agent framework that includes:

- **Planning** - Automatic task breakdown and progress tracking
- **Filesystem Access** - Read/write files, search with grep/glob
- **Shell Execution** - Run commands (with sandboxing)
- **Sub-agents** - Delegate work with isolated contexts
- **Smart Defaults** - Pre-configured prompts and tools
- **Context Management** - Auto-summarization for long conversations

## 🛠️ Customization

### Adding Custom Tools to Vanilla Agent

```python
from langchain_core.tools import tool
from typing import Annotated

@tool
def my_custom_tool(
    input_param: Annotated[str, "Description of parameter"]
) -> str:
    """Tool description that the LLM sees."""
    # Your implementation
    return "result"

# Add to tools list
tools = [calculator, text_analyzer, my_custom_tool]
```

### Token Usage by Tool Count

| Tools | Estimated Tokens |
|-------|------------------|
| 2 tools | ~800 tokens |
| 5 tools | ~1,500 tokens |
| 10 tools | ~2,500 tokens |

Still much less than DeepAgent's 15k!

## 📊 Token Comparison

| Agent Type | System Tokens | Best For |
|------------|---------------|----------|
| **Vanilla** | 500-1,500 | Token limits, custom tools |
| **DeepAgent (minimal)** | 3,000-5,000 | Need some file access |
| **DeepAgent (full)** | 12,000-15,000 | Full features, no token constraints |

See [AGENT_COMPARISON.md](AGENT_COMPARISON.md) for details.

## 🔮 Next Steps: Dynamic Skills

The skill system will enable:

1. **Dynamic Discovery** - Skills auto-loaded from `skills/` folder
2. **Metadata-Driven** - `skills.md` files describe when to use each skill
3. **Zero Code Changes** - Add new skills without modifying core code
4. **LLM-Powered Selection** - Agent chooses the right skill based on context

Example skill metadata (`skills/web_search/skills.md`):
```yaml
name: web_search
description: Search the internet for current information
inputs:
  query: string
outputs:
  results: string
use_when:
  - User asks about current events
  - Need to find recent information
  - Research is required
```

## 📚 Resources

- [DeepAgents Documentation](https://docs.langchain.com/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [Groq API](https://console.groq.com/)

## 📝 License

MIT
