#!/bin/sh
python api.py &
streamlit run App.py --server.port 8501 --server.address 0.0.0.0