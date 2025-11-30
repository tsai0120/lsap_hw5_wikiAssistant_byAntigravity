# System Setup Report

## 1. Containerization

### Single Container Approach
I created a `Dockerfile` that uses `python:3.13-slim` as the base image. It installs `poetry` for dependency management, installs dependencies for both backend and frontend, and then copies the source code. A `start.sh` script is used as the entrypoint to run both `uvicorn` (backend) and `streamlit` (frontend) in the background.

**Dockerfile:**
(See `Dockerfile` in the submission)

### Multi-Container Approach
For better maintainability and separation of concerns, I split the application into two containers:
- **Backend**: Runs the FastAPI server.
- **Frontend**: Runs the Streamlit UI.
A `docker-compose.yml` file orchestrates these services, handling networking and volume mounting for persistent chat history.

## 2. Linux Distributions Comparison

I compared `ubuntu:22.04` and `alpine:3.22` base images.

- **Ubuntu (glibc)**:
  - **Build Time**: Generally faster for Python wheels that have pre-compiled binaries for glibc.
  - **Image Size**: Larger due to more included system libraries.
  - **Compatibility**: High compatibility with most Python packages.

- **Alpine (musl)**:
  - **Build Time**: Can be slower because many Python packages (like `numpy`, `pandas`, `grpcio`) need to be compiled from source for musl libc, as wheels are often not available.
  - **Image Size**: Significantly smaller base image, resulting in a smaller final image if dependencies don't add too much bloat.
  - **Startup Time**: Slightly faster due to smaller size, but application startup is mostly dominated by Python import time.

**Conclusion**: For Data Science/AI applications involving complex C-extensions (like `numpy`, `sentence-transformers`), Ubuntu/Debian slim variants are often preferred over Alpine to avoid compilation headaches and potential performance issues with musl.

## 3. Container Build Speed

I compared two Dockerfile strategies:

1.  **Optimized (Dependencies First)**:
    - `COPY pyproject.toml ...`
    - `RUN poetry install ...`
    - `COPY . .`
    - **Result**: When source code changes, the dependency layer is cached. Rebuilds are very fast (seconds).

2.  **Unoptimized (Source First)**:
    - `COPY . .`
    - `RUN poetry install ...`
    - **Result**: When source code changes, the cache for the `COPY` instruction is invalidated, forcing `poetry install` to run again. Rebuilds are slow (minutes).

**Reason**: Docker uses layer caching. Changing a file invalidates all subsequent layers. By copying frequently changing files (source code) *after* expensive operations (dependency installation), we maximize cache hits.

## 4. Persistent Chat History
I modified `backend/server.py` to save chat history to `chat_history.json`. In the `docker-compose.yml`, I mounted this file as a volume:
```yaml
volumes:
  - ./chat_history.json:/app/chat_history.json
```
This ensures that even if the container is removed, the chat history remains on the host machine.

## 5. Nginx Reverse Proxy
I configured Nginx to listen on port 80 and proxy requests to the frontend container. This allows the application to be accessed via standard HTTP without specifying a port.

```nginx
location / {
    proxy_pass http://localhost:8501;
    ...
}
```
