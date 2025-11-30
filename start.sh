#!/bin/bash
# Start Backend
cd /app/backend
uvicorn server:app --host 0.0.0.0 --port 8000 &

# Start Frontend
cd /app/frontend
streamlit run chat.py --server.port 8501 --server.address 0.0.0.0 &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?
