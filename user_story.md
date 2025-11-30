# User Story: Multi-Language Support

## Persona
**Name**: Li-Wei
**Role**: A Mandarin-speaking researcher and student.
**Goal**: To quickly find information about local history and culture which is more abundant in Chinese Wikipedia than in English Wikipedia.

## Problem
The current Wiki Assistant only searches English Wikipedia. When Li-Wei asks questions about "Taipei 101" or "Sun Yat-sen" in Chinese, the assistant searches English Wikipedia, which might lack specific local context or nuances available in the Chinese entries. Furthermore, the retrieved content is in English, requiring mental translation.

## Solution
Implement a **Language Selector** in the Wiki Assistant UI.
- Users can select their preferred language (e.g., English, Chinese, Spanish, etc.).
- The backend will direct search queries to the corresponding Wikipedia subdomain (e.g., `zh.wikipedia.org`).
- The assistant will retrieve and process text from the selected language's Wikipedia.

## Evaluation
1. **Setup**: Select "zh" (Chinese) from the language dropdown.
2. **Action**: Ask "Who is the current president of Taiwan?" (in Chinese: "台灣現任總統是誰？").
3. **Expected Result**: The assistant searches `zh.wikipedia.org`, retrieves the article for "中華民國總統" or similar, and answers in Chinese with up-to-date information from the Chinese source.
4. **Verification**: The response cites Chinese Wikipedia pages and provides accurate local information.
