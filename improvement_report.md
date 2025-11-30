# Improvement Report (Bonus)

## User Story: Multi-Language Support

### 1. Persona & Task
**Persona**: Li-Wei, a Mandarin-speaking researcher.
**Task**: Find information about local Taiwanese history and culture using the Wiki Assistant.

### 2. Problem
The original system was hardcoded to search English Wikipedia (`en.wikipedia.org`). When Li-Wei asked questions in Chinese or about local topics, the assistant searched English content, which often lacked depth on local subjects or returned English results that required translation.

### 3. Solution
I implemented a **Language Selector** in the frontend and updated the backend to support dynamic Wikipedia language targeting.

**Changes:**
- **Frontend**: Added a `st.sidebar.selectbox` to let the user choose between English, Chinese, Spanish, etc.
- **Agent**: Updated `WikiAssistantAgent` to accept the selected language and pass it to the search tool.
- **Backend**: Updated `search_for_wikipedia_page_url` to accept a `language` parameter and query the appropriate subdomain (e.g., `zh.wikipedia.org`).
- **Utils**: Improved `get_wiki_text_from_url` to handle mobile URL conversion generically for any language subdomain.

### 4. Evaluation
I verified the improvement by:
1.  Selecting "zh" (Chinese) in the UI.
2.  Asking "台灣的最高峰是哪一座？" (What is the highest peak in Taiwan?).
3.  The assistant correctly searched Chinese Wikipedia, retrieved the page for "玉山" (Yushan), and provided an answer in Traditional Chinese citing the correct source.

(Insert Screenshot of Chinese search result here)
