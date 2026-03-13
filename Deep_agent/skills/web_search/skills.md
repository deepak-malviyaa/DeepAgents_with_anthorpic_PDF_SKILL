name: web_search
description: Search the internet for information, print results to the screen, and save them to a file
inputs:
  query: string
outputs:
  - results
  - saved_file
use_when:
  - User asks to search the web
  - User needs current information not in your training data
  - User asks about recent events or news
  - User wants to find information online
  - User wants to save search results to a file
