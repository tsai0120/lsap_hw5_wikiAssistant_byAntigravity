# 改進報告 (Improvement Report - Bonus)

## 使用者故事：多語言支持 (User Story: Multi-Language Support)

### 1. 人物與任務 (Persona & Task)
**人物**: 立偉 (Li-Wei)，一位母語為中文的研究人員。
**任務**: 使用 Wiki Assistant 查找有關台灣在地歷史和文化的資訊。

### 2. 問題 (Problem)
原始系統被寫死 (Hardcoded) 只能搜尋英文維基百科 (`en.wikipedia.org`)。當立偉用中文提問，或詢問有關台灣在地的特定的主題時，助手只能搜尋英文內容。這導致：
1.  搜尋結果缺乏在地觀點或詳細資訊 (例如台灣特定的地名、歷史事件)。
2.  回傳的內容是英文，需要額外的心力進行翻譯。

### 3. 解決方案 (Solution)
我實作了 **多語言選擇器 (Language Selector)** 和 **多會話管理 (Session Management)**。

**實作細節:**

- **前端 (Frontend)**:
  - 在側邊欄新增 `st.selectbox`，讓使用者選擇目標語言 (如中文、英文、日文等)。
  - 實作 **i18n (國際化)** 機制，介面上的標籤 (如 "Settings", "New Chat") 會根據選擇的語言自動切換。
  - 新增 **會話管理** 功能，使用者可以創建多個對話，系統會自動根據第一則訊息生成標題。

- **Agent (DSPy)**:
  - 更新 `WikiAssistantAgent` 的簽名 (Signature)，新增 `language` 欄位。
  - 在 `forward` 方法中，將使用者選擇的語言代碼傳遞給 Agent，確保 Agent 理解當前的語言上下文。

- **後端 (Backend)**:
  - 更新 `search_for_wikipedia_page_url` 函數，接受 `language` 參數，並動態構建維基百科 API URL (例如 `https://zh.wikipedia.org/w/api.php`)。
  - 優化 `get_wiki_text_from_url` 函數，使其能通用的處理各國語言的行動版網頁 (`.m.wikipedia.org`) 轉址，增強爬蟲的穩定性。
  - 重構資料儲存結構，從單純的列表改為基於 Session ID 的字典結構，支援多個獨立的對話記錄。

### 4. 評估 (Evaluation)
我透過以下步驟驗證了改進：
1.  在 UI 中選擇 "Traditional Chinese (繁體中文)"。
2.  詢問：「台灣的最高峰是哪一座？」。
3.  **結果**: 助手正確搜尋了中文維基百科，檢索到「玉山」的頁面，並用繁體中文回答：「台灣的最高峰是玉山，主峰海拔 3,952 公尺...」。
4.  **介面**: 側邊欄的按鈕和標題也都正確顯示為中文，提供了完整的一致性體驗。

(請在此處插入中文搜尋結果的截圖)
