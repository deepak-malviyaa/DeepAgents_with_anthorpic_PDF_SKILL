"""
Text Summarizer Skill

Extracts key information from text.
"""


def run(text: str) -> str:
    """
    Summarize text by extracting key information.
    
    This is a simple rule-based implementation. For better results,
    use an LLM-based summarization API.
    
    Args:
        text: Text to summarize
    
    Returns:
        Summary of the text
    """
    # Simple extractive summarization
    sentences = text.split('.')
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Basic statistics
    word_count = len(text.split())
    char_count = len(text)
    sentence_count = len(sentences)
    
    # Extract first and last sentences as summary
    if sentence_count == 0:
        return "No content to summarize."
    elif sentence_count == 1:
        summary = sentences[0]
    elif sentence_count == 2:
        summary = ' '.join(sentences)
    else:
        # Take first sentence and last sentence
        summary = f"{sentences[0]}... {sentences[-1]}"
    
    return f"""Text Summary:

📊 Statistics:
- Words: {word_count}
- Characters: {char_count}
- Sentences: {sentence_count}

📝 Summary:
{summary}

Note: This is a basic rule-based summary. For advanced summarization:
1. Use an LLM API (OpenAI, Claude, etc.)
2. Or use transformer models (BART, T5, etc.)
"""
