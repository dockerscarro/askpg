Here is the updated Python code:

import streamlit as st
import os
import tempfile
import uuid
import re
import json
import bisect
import numpy as np
import psycopg2
from collections import defaultdict
from sentence_transformers import SentenceTransformer
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from datetime import datetime, timezone
from dateutil import parser
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

# ... rest of the code ...

st.set_page_config(page_title="Hybrid Log Search", layout="wide")
st.title("📚 Hybrid Log Search (Qdrant) ")

uploaded_file = st.sidebar.file_uploader("📁 Upload a .txt, .pdf, or .docx file", type=["txt", "pdf", "docx"])

if uploaded_file:
    if "uploaded_file_name" not in st.session_state or st.session_state.uploaded_file_name != uploaded_file.name:
        with st.spinner("📥 Parsing and inserting logs into database..."):
            parsed_entries = load_and_parse_file(uploaded_file)
            ensure_table_exists()
            st.info("Table is ready")
            # Now insert logs
            inserted_count = insert_logs_pg(parsed_entries)
            
            if inserted_count > 0:
                st.success(f"✅ Inserted {inserted_count} new log entries into PostgreSQL.")
                st.session_state.indexed = False 
            else:
                st.info("ℹ️ No new entries inserted. Skipping indexing.")

            st.session_state.uploaded_file_name = uploaded_file.name
            st.session_state.uploaded_handled = True

    if not st.session_state.get("indexed", False):
        with st.spinner("⚙️ Indexing logs for search..."):
            all_logs = load_logs_from_db()
            index_texts(all_logs)
            cluster_status = st.empty()         
            build_text_loglevel_clusters_v2()         
            st.session_state.indexed = True
            st.success("✅ Indexing complete and ready for querying.")

else:
    st.info("📂 Please upload a file to insert and index logs.")

query = st.text_input("🔎 paste any log message:")
search_clicked = st.button("Search")

# ... rest of the code ...

This code moves the file upload control to the left sidebar by replacing `st.file_uploader` with `st.sidebar.file_uploader`. The rest of the code remains the same.