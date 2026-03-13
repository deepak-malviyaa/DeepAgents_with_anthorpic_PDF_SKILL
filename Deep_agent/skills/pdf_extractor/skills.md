name: pdf_extractor
description: Extract text and metadata from a PDF file given its file path. ALWAYS use this when the user provides a path ending in .pdf or mentions a PDF file - even if they say 'summarize' or 'read'.
inputs:
  query: string
outputs:
  - extracted_text
  - saved_file
use_when:
  - Input is a file path ending in .pdf
  - User says read, open, extract, summarize, or analyze a PDF
  - User provides a Windows or Unix file path and the file is a PDF
  - Any message containing '.pdf'
  - User wants to save PDF contents to a file
