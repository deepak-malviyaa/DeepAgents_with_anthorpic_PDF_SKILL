name: text_summarizer
description: Summarize plain text content into concise key points. Do NOT use for PDF files or file paths — use pdf_extractor for those.
inputs:
  text: string
outputs:
  - summary
use_when:
  - User pastes plain text and wants a summary
  - User provides a block of text (not a file) and wants key points
  - User wants to condense a piece of writing they typed or pasted
never_use_when:
  - The input looks like a file path (contains \ or / or ends in .pdf .txt .docx)
  - User mentions a PDF file or provides a file path
