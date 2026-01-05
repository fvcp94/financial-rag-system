"""Streamlit UI for Financial RAG System - Dark Theme with BRIGHT Visible Sidebar"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.rag_pipeline import RAGPipeline
from src.vector_store import VectorStoreManager
from src.data_ingestion import DocumentProcessor

# Page configuration
st.set_page_config(
    page_title="Financial RAG System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Beautiful Dark Theme CSS with ULTRA BRIGHT Sidebar
st.markdown("""
<style>
    /* Dark theme colors */
    :root {
        --primary-color: #00d4ff;
        --secondary-color: #7c3aed;
        --accent-color: #f59e0b;
    }
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* ========== SIDEBAR - ULTRA BRIGHT & VISIBLE ========== */
    
    /* Sidebar background with gradient */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #1e293b 50%, #0f172a 100%) !important;
        border-right: 3px solid #00d4ff !important;
        box-shadow: 4px 0 20px rgba(0, 212, 255, 0.3) !important;
    }
    
    /* ALL sidebar text - BRIGHT WHITE */
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Sidebar main headers (###) - BRIGHT CYAN WITH GLOW */
    section[data-testid="stSidebar"] h3 {
        color: #00d4ff !important;
        font-weight: 800 !important;
        font-size: 1.4rem !important;
        text-shadow: 0 0 15px rgba(0, 212, 255, 0.8), 0 0 30px rgba(0, 212, 255, 0.4) !important;
        margin: 1.5rem 0 1rem 0 !important;
        padding: 0.5rem 0 !important;
        border-bottom: 2px solid rgba(0, 212, 255, 0.3) !important;
    }
    
    /* Sidebar subheaders (####) - BRIGHT PURPLE */
    section[data-testid="stSidebar"] h4 {
        color: #a78bfa !important;
        font-weight: 700 !important;
        font-size: 1.15rem !important;
        text-shadow: 0 0 10px rgba(167, 139, 250, 0.6) !important;
        margin: 1rem 0 0.5rem 0 !important;
    }
    
    /* Sidebar labels - EXTRA BRIGHT */
    section[data-testid="stSidebar"] label {
        color: #f0f9ff !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        text-shadow: 0 0 5px rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Sidebar select boxes - BRIGHT with GLOW */
    section[data-testid="stSidebar"] select,
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background: linear-gradient(135deg, #1e40af 0%, #1e293b 100%) !important;
        color: #ffffff !important;
        border: 2px solid #00d4ff !important;
        border-radius: 0.5rem !important;
        font-weight: 600 !important;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.3) !important;
    }
    
    /* Sidebar select box hover */
    section[data-testid="stSidebar"] .stSelectbox > div > div:hover {
        border-color: #7c3aed !important;
        box-shadow: 0 0 20px rgba(124, 58, 237, 0.5) !important;
    }
    
    /* Sidebar metrics - BRIGHT */
    section[data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: #00d4ff !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.6) !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        color: #e0e7ff !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="stMetricDelta"] {
        color: #10b981 !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar divider - GLOWING */
    section[data-testid="stSidebar"] hr {
        border-color: rgba(0, 212, 255, 0.5) !important;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.3) !important;
        margin: 1rem 0 !important;
    }
    
    /* Sidebar caption - VISIBLE */
    section[data-testid="stSidebar"] .caption {
        color: #94a3b8 !important;
        font-size: 0.9rem !important;
        text-align: center !important;
    }
    
    /* Sidebar expander - BRIGHT */
    section[data-testid="stSidebar"] .streamlit-expanderHeader {
        background: linear-gradient(135deg, #1e40af 0%, #1e293b 100%) !important;
        border: 2px solid rgba(0, 212, 255, 0.4) !important;
        border-radius: 0.5rem !important;
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    section[data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        border-color: #00d4ff !important;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.4) !important;
    }
    
    /* Sidebar sliders - VISIBLE */
    section[data-testid="stSidebar"] .stSlider > div > div > div {
        background: #00d4ff !important;
    }
    
    section[data-testid="stSidebar"] .stSlider label {
        color: #f0f9ff !important;
    }
    
    /* Sidebar checkboxes - BRIGHT */
    section[data-testid="stSidebar"] .stCheckbox label {
        color: #f0f9ff !important;
        font-weight: 500 !important;
    }
    
    section[data-testid="stSidebar"] input[type="checkbox"] {
        border: 2px solid #00d4ff !important;
    }
    
    /* ========== END SIDEBAR STYLING ========== */
    
    /* Main header with gradient */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00d4ff 0%, #7c3aed 50%, #f59e0b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 2rem 0;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { filter: drop-shadow(0 0 10px rgba(0, 212, 255, 0.5)); }
        to { filter: drop-shadow(0 0 20px rgba(124, 58, 237, 0.8)); }
    }
    
    .subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Answer card with gradient border */
    .answer-card {
        background: linear-gradient(135deg, #1e293b 0%, #2d3748 100%);
        border-left: 4px solid;
        border-image: linear-gradient(180deg, #00d4ff, #7c3aed) 1;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        color: #f1f5f9;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    /* Upload area styling */
    .upload-area {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 2px dashed rgba(0, 212, 255, 0.5);
        border-radius: 1rem;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: rgba(0, 212, 255, 1);
        background: linear-gradient(135deg, #334155 0%, #1e293b 100%);
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.2);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4), 0 0 20px rgba(0, 212, 255, 0.3);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-radius: 0.5rem 0.5rem 0 0;
        color: #94a3b8;
        border: 1px solid rgba(0, 212, 255, 0.2);
        padding: 0.75rem 1.5rem;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%);
        color: white;
        border-color: transparent;
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        color: #00d4ff;
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-radius: 0.5rem;
        border: 1px solid rgba(0, 212, 255, 0.2);
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.2) 100%);
        border-left: 4px solid #10b981;
        color: #10b981;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.2) 100%);
        border-left: 4px solid #ef4444;
        color: #ef4444;
    }
    
    /* Text input styling */
    .stTextArea textarea {
        background: #1e293b;
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 0.5rem;
        color: #f1f5f9;
    }
    
    .stTextArea textarea:focus {
        border-color: #00d4ff;
        box-shadow: 0 0 0 1px #00d4ff;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'rag_pipeline' not in st.session_state:
    try:
        with st.spinner("🔄 Initializing RAG Pipeline..."):
            st.session_state.rag_pipeline = RAGPipeline()
            st.session_state.vs_manager = VectorStoreManager()
            st.session_state.doc_processor = DocumentProcessor()
        st.success("✅ RAG Pipeline initialized successfully!")
    except Exception as e:
        st.error(f"❌ Error initializing RAG pipeline: {e}")
        st.stop()

if 'query_history' not in st.session_state:
    st.session_state.query_history = []

# Sidebar with BRIGHT visible text
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    # Filters
    st.markdown("#### 📋 Filters")
    
    st.markdown("**Company:**")
    company = st.selectbox(
        "Select Company",
        ["All", "Apple", "Microsoft", "Google", "Amazon", "Meta", "Tesla", "NVIDIA"],
        index=0,
        help="Filter documents by company",
        label_visibility="collapsed"
    )
    
    st.markdown("**Year:**")
    year = st.selectbox(
        "Select Year",
        ["All", "2024", "2023", "2022", "2021"],
        index=0,
        help="Filter documents by year",
        label_visibility="collapsed"
    )
    
    st.markdown("**Quarter:**")
    quarter = st.selectbox(
        "Select Quarter",
        ["All", "Q1", "Q2", "Q3", "Q4", "Annual"],
        index=0,
        help="Filter documents by quarter",
        label_visibility="collapsed"
    )
    
    # Advanced settings
    with st.expander("🔧 Advanced Settings"):
        top_k = st.slider(
            "Documents to retrieve",
            min_value=1,
            max_value=10,
            value=4,
            help="Number of relevant documents to retrieve"
        )
        
        show_metadata = st.checkbox("Show detailed metadata", value=True)
        show_costs = st.checkbox("Show cost metrics", value=True)
    
    st.divider()
    
    # System stats with bright text
    st.markdown("#### 📊 System Stats")
    try:
        stats = st.session_state.vs_manager.get_collection_stats()
        cost_summary = st.session_state.rag_pipeline.get_cost_summary()
        
        st.metric("📚 Documents", stats.get("total_documents", 0))
        st.metric("🔍 Queries Today", cost_summary.get("query_count", 0))
        
        if show_costs:
            st.metric(
                "💰 Cost", 
                f"${cost_summary.get('total_cost', 0):.4f}",
                delta="100% FREE"
            )
    except Exception as e:
        st.error(f"Stats unavailable")
    
    st.divider()
    st.caption("🚀 Built with LangChain • OpenRouter (FREE) • Streamlit")

# Main content
st.markdown('<div class="main-header">📊 Financial Earnings RAG System</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">🤖 AI-Powered Financial Document Analysis • 100% FREE • Lightning Fast ⚡</div>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["💬 Query", "📤 Upload", "📈 Analytics", "ℹ️ About"])

# [REST OF THE TABS CODE - SAME AS BEFORE]
# Keeping previous tab implementations...

with tab1:
    st.markdown("### 🔍 Ask a Question")
    
    query = st.text_area(
        "Enter your question:",
        placeholder="e.g., What were Apple's Q3 2024 revenue drivers?",
        height=100
    )
    
    st.markdown("**💡 Example queries:**")
    col1, col2, col3 = st.columns(3)
    
    examples = [
        "What were the key risk factors?",
        "Summarize revenue performance",
        "What are future growth plans?"
    ]
    
    for idx, (col, example) in enumerate(zip([col1, col2, col3], examples)):
        if col.button(example, key=f"ex_{idx}", use_container_width=True):
            query = example
    
    if st.button("🔎 Search", type="primary", use_container_width=True):
        if query:
            with st.spinner("🤔 Analyzing..."):
                filters = {}
                if company != "All":
                    filters["company"] = company
                if year != "All":
                    filters["year"] = int(year)
                if quarter != "All":
                    filters["quarter"] = quarter
                
                response = st.session_state.rag_pipeline.query(
                    question=query,
                    filters=filters if filters else None,
                    top_k=top_k
                )
                
                st.session_state.query_history.append({
                    "timestamp": datetime.now(),
                    "query": query,
                    "response": response,
                    "filters": filters
                })
                
                st.divider()
                st.markdown("### 💡 Answer")
                st.markdown(f"<div class='answer-card'>{response['answer']}</div>", unsafe_allow_html=True)
                
                if response['sources']:
                    st.markdown(f"### 📚 Sources ({len(response['sources'])} docs)")
                    for idx, source in enumerate(response['sources'], 1):
                        with st.expander(f"📄 {source['company']} - {source['quarter']} {source['year']}", expanded=idx==1):
                            st.text(source['content'])
                
                if response.get('metrics'):
                    st.markdown("### 📊 Metrics")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("⚡ Latency", f"{response.get('metrics', {}).get('latency', 0):.2f}s")
                    c2.metric("📄 Docs", response.get('metrics', {}).get('retrieved_docs', 0))
                    c3.metric("🔤 Tokens", f"{response.get('metrics', {}).get('total_tokens', 0):,}")
                    c4.metric("💰 Cost", f"${response.get('metrics', {}).get('total_cost', 0):.6f}")
        else:
            st.warning("⚠️ Please enter a question")

with tab2:
    st.markdown("### 📤 Upload Documents")
    
    st.markdown("""
    <div class='upload-area'>
        <h3>📁 Drag and Drop Files</h3>
        <p style='color: #94a3b8;'>PDF & DOCX • Max 200MB</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'docx'])
    
    if uploaded_file:
        st.success(f"✅ {uploaded_file.name}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            doc_company = st.selectbox("Company", ["Apple", "Microsoft", "Google", "Amazon", "Meta"], key="uc")
        with col2:
            doc_year = st.number_input("Year", 2020, 2025, 2024, key="uy")
        with col3:
            doc_quarter = st.selectbox("Quarter", ["Q1", "Q2", "Q3", "Q4"], key="uq")
        
        if st.button("🚀 Upload", type="primary", use_container_width=True):
            with st.spinner("Processing..."):
                try:
                    temp_path = Path(f"/tmp/{uploaded_file.name}")
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    chunks = st.session_state.doc_processor.process_pdf(
                        pdf_path=str(temp_path),
                        metadata={
                            "company": doc_company,
                            "year": doc_year,
                            "quarter": doc_quarter
                        }
                    )
                    
                    st.session_state.vs_manager.add_documents(chunks)
                    stats = st.session_state.vs_manager.get_collection_stats()
                    
                    st.success(f"🎉 Uploaded! {stats['total_documents']} total docs")
                    temp_path.unlink()
                except Exception as e:
                    st.error(f"❌ Error: {e}")

with tab3:
    st.markdown("### 📈 Analytics")
    if st.session_state.query_history:
        st.info(f"📊 {len(st.session_state.query_history)} queries in session")
    else:
        st.info("📭 No queries yet")

with tab4:
    st.markdown("### ℹ️ About")
    st.markdown("""
    **Financial RAG System** - Production-ready AI document analysis
    
    **Features:**
    - 🤖 Free LLM (Llama 3.2 3B)
    - 💾 Local Embeddings
    - 📤 Easy Upload
    - ⚡ Fast Queries
    - 💰 $0.00 Cost
    """)

st.divider()
st.markdown("""
<div style='text-align: center; padding: 1rem;'>
    <p style='background: linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%); 
              -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700;'>
        Financial RAG System v1.0
    </p>
</div>
""", unsafe_allow_html=True)
