# Wiki Assistant (維基百科助手)

這是一個基於 RAG (檢索增強生成) 的 AI 助手，可以回答有關維基百科條目的問題。它使用 Google Gemini 模型來生成回答，並通過檢索維基百科的內容來增強準確性。

## 功能特色

- **智能問答**：使用 Gemini 2.5 Flash 模型回答問題。
- **多語言支持 (Bonus)**：支持多種語言的維基百科搜索，且**介面語言會隨之切換**。
- **多會話管理**：支持創建多個聊天會話，並在側邊欄進行切換和管理。
- **用戶個性化**：可在側邊欄設定使用者名稱，系統會記住您的稱呼。
- **持久化聊天記錄**：所有會話記錄都會自動保存。
- **Docker 部署**：支持單容器和多容器部署，並包含 Nginx 反向代理配置。

## 快速開始

### 1. 環境設置

首先，請確保您已安裝 Docker 和 Docker Compose。

複製環境變量範例文件並填入您的 Google AI Studio API Key：

```bash
cp .env.example .env
# 編輯 .env 文件，填入您的 GEMINI_API_KEY
```

### 2. 啟動應用 (推薦)

使用 Docker Compose 啟動所有服務 (包含 Frontend, Backend, Nginx)：

```bash
docker-compose up --build
```

啟動後，您可以訪問以下服務：

- **Frontend (前端)**: http://localhost:9500
- **Backend (後端)**: http://localhost:9000
- **Nginx (反向代理)**: http://localhost:8080

### 3. 使用說明

1. 打開瀏覽器訪問 http://localhost:9500 (或 http://localhost:8080)。
2. 在左側側邊欄選擇您想要搜尋的維基百科語言 (例如 "zh" 代表中文)。
3. 在聊天框中輸入您的問題。

## 實作細節

### 系統架構

- **Frontend**: 使用 Streamlit 構建，負責 UI 展示和與用戶交互。使用 DSPy 框架構建 Agent 邏輯。
- **Backend**: 使用 FastAPI 構建，負責處理維基百科的搜索和內容爬取。
- **Database**: 使用 JSON 文件 (`data/chat_history.json`) 進行簡單的持久化存儲。
- **Nginx**: 作為反向代理，將請求轉發到前端容器。

### 改進與優化 (Bonus)

為了提升非英語用戶的體驗，我實作了**多語言支持**功能：

1. **前端改進**：在 Sidebar 新增了語言選擇器。
2. **Agent 優化**：`WikiAssistantAgent` 現在可以接受語言參數，並將其傳遞給搜索工具。
3. **後端增強**：
    - `search_for_wikipedia_page_url` 函數新增 `language` 參數，可動態查詢不同語言的維基百科子網域 (如 `zh.wikipedia.org`)。
    - `get_wiki_text_from_url` 函數優化了對移動版網頁 (`.m.wikipedia.org`) 的處理邏輯，使其適用於所有語言版本。

### 遇到的問題與解決

在開發過程中，遇到了 Docker Volume 掛載單個文件 (`chat_history.json`) 導致的權限和目錄誤判問題。
**解決方案**：改為掛載 `data/` 目錄，將聊天記錄文件放在目錄中，這樣 Docker 就不會錯誤地將其創建為目錄，並且更容易管理權限。

## 開發者指南

### 單容器模式

如果您只想運行一個容器：

```bash
docker build -t wiki-assistant .
docker run -p 9000:8000 -p 9500:8501 --env-file .env wiki-assistant
```

### 目錄結構

```
wiki-assistant/
├── backend/            # FastAPI 後端代碼
├── frontend/           # Streamlit 前端代碼
├── data/               # 持久化數據目錄
├── docker-compose.yml  # Docker Compose 配置
├── Dockerfile*         # 各種 Dockerfile 配置
├── nginx.conf          # Nginx 配置
└── README.md           # 項目文檔
```
