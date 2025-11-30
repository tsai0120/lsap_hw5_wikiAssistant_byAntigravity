# 系統建置報告 (System Setup Report)

## 1. 容器化 (Containerization)

### 單一容器方法 (Single Container Approach)
我建立了一個 `Dockerfile`，使用 `python:3.13-slim` 作為基礎映像檔。它安裝了 `poetry` 進行依賴管理，分別安裝後端和前端的依賴套件，最後複製程式碼。我使用了一個 `start.sh` 腳本作為進入點 (Entrypoint)，在背景同時啟動 `uvicorn` (後端) 和 `streamlit` (前端)。

**Dockerfile 實作細節:**
- 使用 `python:3.13-slim` 保持映像檔輕量。
- 設定 `POETRY_VIRTUALENVS_CREATE=false` 以便將套件直接安裝在系統環境中。
- 透過 `start.sh` 腳本管理多個進程，並使用 `wait -n` 確保若任一服務崩潰，容器會正確退出。

### 多容器方法 (Multi-Container Approach)
為了更好的維護性和職責分離，我將應用程式拆分為兩個容器：
- **Backend**: 運行 FastAPI 伺服器，負責處理邏輯和數據。
- **Frontend**: 運行 Streamlit UI，負責與使用者互動。
使用 `docker-compose.yml` 來編排這些服務，處理網路連接 (Networking) 和數據持久化 (Volume Mounting)。

## 2. Linux 發行版比較 (Linux Distributions Comparison)

我比較了 `ubuntu:22.04` 和 `alpine:3.22` 兩種基礎映像檔。

- **Ubuntu (glibc)**:
  - **建置時間**: 通常較快，因為大多數 Python 套件 (Wheels) 都有預先編譯好的 glibc 二進位檔。
  - **映像檔大小**: 較大，因為包含了更多的系統函式庫。
  - **相容性**: 高，幾乎支援所有 Python 套件。

- **Alpine (musl)**:
  - **建置時間**: 可能較慢，因為許多 Python 套件 (如 `numpy`, `pandas`) 需要針對 musl libc 從原始碼編譯。
  - **映像檔大小**: 基礎映像檔非常小，最終映像檔通常也較小。
  - **啟動時間**: 由於體積小，啟動稍快，但應用程式啟動時間主要取決於 Python import 速度。

**結論**: 對於涉及複雜 C 擴展的 Data Science/AI 應用，Ubuntu/Debian slim 版本通常優於 Alpine，因為可以避免編譯問題和潛在的效能問題。

## 3. 容器建置速度比較 (Container Build Speed)

我比較了兩種 Dockerfile 策略：

1.  **最佳化 (Optimized - Dependencies First)**:
    - 先 `COPY pyproject.toml ...`
    - 執行 `RUN poetry install ...`
    - 最後 `COPY . .`
    - **結果**: 當原始碼改變時，依賴層 (Dependency Layer) 會被快取 (Cached)。重新建置非常快 (秒級)。

2.  **未最佳化 (Unoptimized - Source First)**:
    - 先 `COPY . .`
    - 執行 `RUN poetry install ...`
    - **結果**: 當原始碼改變時，`COPY` 指令後的快取失效，迫使 `poetry install` 重新執行。重新建置非常慢 (分鐘級)。

**原因**: Docker 使用分層快取 (Layer Caching)。改變檔案會使後續所有層失效。將變動頻繁的檔案 (原始碼) 放在耗時操作 (安裝依賴) 之後，可以最大化快取命中率。

## 4. 持久化聊天記錄 (Persistent Chat History)
我修改了 `backend/server.py`，將聊天記錄儲存在 `data/chat_history.json`。在 `docker-compose.yml` 中，我掛載了這個目錄：
```yaml
volumes:
  - ./data:/app/data
```
這確保了即使容器被刪除，聊天記錄仍然保留在主機 (Host) 上。使用目錄掛載而非單一檔案掛載，解決了 Docker 可能將檔案誤認為目錄的權限問題。

## 5. Nginx 反向代理 (Nginx Reverse Proxy)
我配置了 Nginx 容器作為反向代理，監聽 80 埠 (映射到主機 8080)，並將請求轉發到前端容器。

```nginx
location / {
    proxy_pass http://frontend:8501;
    ...
}
```
這允許應用程式透過標準 HTTP 存取，並隱藏了內部的服務架構。
