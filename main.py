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

# ... (rest of the code remains the same)

st.set_page_config(page_title="Hybrid Log Search", layout="wide")
st.title("📚 Hybrid Log Search (Qdrant) ")

uploaded_file = st.sidebar.file_uploader("📁 Upload a .txt, .pdf, or .docx file", type=["txt", "pdf", "docx"])

# ... (rest of the code remains the same)

In the updated code, I replaced `st.file_uploader` with `st.sidebar.file_uploader` to move the file upload controls to the left sidebar.