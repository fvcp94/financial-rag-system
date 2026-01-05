"""Streamlit UI for Financial RAG System - PERFECT Light Theme - All Issues Fixed"""

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

# PERFECT Light Theme CSS - ALL VISIBILITY ISSUES FIXED
st.markdown("""
<style>
    /* Light theme colors */
    :root {
        --primary: #0066cc;
        --secondary: #7c3aed;
        --accent: #f59e0b;
        --success: #059669;
        --bg-light: #f8fafc;
        --bg-white: #ffffff;
        --text-dark: #0f172a;
        --text-gray: #475569;
        --border: #e2e8f0;
    }
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
    }
    
    /* ========== SIDEBAR STYLING ========== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%) !important;
        border-right: 3px solid var(--primary) !important;
        box-shadow: 4px 0 20px rgba(0, 102, 204, 0.1) !important;
    }
    
    section[data-testid="stSidebar"] h3 {
        color: var(--primary) !important;
        font-weight: 800 !important;
        font-size: 1.4rem !important;
        margin: 1.5rem 0 1rem 0 !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 3px solid var(--primary) !important;
    }
    
    section[data-testid="stSidebar"] h4 {
        color: var(--secondary) !important;
        font-weight: 700 !important;
        font-size: 1.15rem !important;
        margin: 1rem 0 0.5rem 0 !important;
    }
    
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {
        color: var(--text-dark) !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    section[data-testid="stSidebar"] select,
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background: white !important;
        color: var(--text-dark) !important;
        border: 2px solid var(--primary) !important;
        border-radius: 0.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox > div > div:hover {
        border-color: var(--secondary) !important;
        box-shadow: 0 4px 8px rgba(124, 58, 237, 0.2) !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: var(--primary) !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        color: var(--text-gray) !important;
        font-weight: 600 !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="stMetricDelta"] {
        color: var(--success) !important;
        font-weight: 700 !important;
    }
    
    section[data-testid="stSidebar"] hr {
        border-color: var(--border) !important;
        border-width: 2px !important;
        margin: 1.5rem 0 !important;
    }
    
    section[data-testid="stSidebar"] .streamlit-expanderHeader {
        background: white !important;
        border: 2px solid var(--border) !important;
        border-radius: 0.5rem !important;
        color: var(--text-dark) !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    }
    
    section[data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        border-color: var(--primary) !important;
        background: #f8fafc !important;
    }
    
    section[data-testid="stSidebar"] .stSlider > div > div > div {
        background: var(--primary) !important;
    }
    
    section[data-testid="stSidebar"] .stCheckbox label {
        color: var(--text-dark) !important;
        font-weight: 600 !important;
    }
    
    section[data-testid="stSidebar"] input[type="checkbox"] {
        border: 2px solid var(--primary) !important;
    }
    
    section[data-testid="stSidebar"] .caption {
        color: var(--text-gray) !important;
        font-size: 0.85rem !important;
        text-align: center !important;
        font-weight: 500 !important;
    }
    
    /* ========== MAIN CONTENT ========== */
    
    /* Main header */
    .main-header {
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #0066cc 0%, #7c3aed 50%, #f59e0b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 2rem 0 1rem 0;
        filter: drop-shadow(0 4px 6px rgba(0, 102, 204, 0.2));
    }
    
    .subtitle {
        text-align: center;
        color: var(--text-gray);
        font-size: 1.2rem;
        font-weight: 500;
        margin-bottom: 2rem;
    }
    
    /* Answer card */
    .answer-card {
        background: white;
        border-left: 5px solid var(--primary);
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        color: var(--text-dark);
        font-size: 1.1rem;
        line-height: 1.8;
    }
    
    /* Upload area */
    .upload-area {
        background: linear-gradient(135deg, #f8fafc 0%, white 100%);
        border: 3px dashed var(--primary);
        border-radius: 1rem;
        padding: 3rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: var(--secondary);
        background: linear-gradient(135deg, white 0%, #f8fafc 100%);
        box-shadow: 0 8px 16px rgba(124, 58, 237, 0.1);
    }
    
    .upload-area h3 {
        color: var(--primary);
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    /* ========== BUTTONS - FIXED FOR VISIBILITY ========== */
    
    /* ALL buttons - default style */
    .stButton>button {
        background: linear-gradient(135deg, #0066cc 0%, #7c3aed 100%) !important;
        color: #ffffff !important;  /* FORCE WHITE TEXT */
        border: none !important;
        border-radius: 0.5rem !important;
        padding: 0.75rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 6px rgba(0, 102, 204, 0.3) !important;
        transition: all 0.3s ease !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2) !important;  /* Text shadow for better visibility */
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(124, 58, 237, 0.4) !important;
        color: #ffffff !important;  /* KEEP WHITE ON HOVER */
    }
    
    .stButton>button:active {
        color: #ffffff !important;  /* KEEP WHITE WHEN CLICKED */
    }
    
    .stButton>button:focus {
        color: #ffffff !important;  /* KEEP WHITE WHEN FOCUSED */
    }
    
    /* Make sure button text is ALWAYS visible */
    .stButton>button * {
        color: #ffffff !important;
    }
    
    /* ========== END BUTTON FIXES ========== */
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 0.5rem 0.5rem 0 0;
        color: var(--text-gray);
        border: 2px solid var(--border);
        border-bottom: none;
        padding: 0.75rem 1.5rem;
        font-weight: 700;
        font-size: 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0066cc 0%, #7c3aed 100%);
        color: white;
        border-color: transparent;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: var(--primary);
        font-size: 2.2rem;
        font-weight: 800;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-gray);
        font-weight: 600;
        font-size: 1rem;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 0.5rem;
        border: 2px solid var(--border);
        color: var(--text-dark);
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .streamlit-expanderHeader:hover {
        border-color: var(--primary);
        background: #f8fafc;
    }
    
    /* Success/Error/Warning/Info messages */
    .stSuccess {
        background: linear-gradient(135deg, rgba(5, 150, 105, 0.1) 0%, rgba(5, 150, 105, 0.05) 100%);
        border-left: 5px solid var(--success);
        border-radius: 0.5rem;
        padding: 1rem;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%);
        border-left: 5px solid #ef4444;
        border-radius: 0.5rem;
        padding: 1rem;
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%);
        border-left: 5px solid var(--accent);
        border-radius: 0.5rem;
        padding: 1rem;
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(0, 102, 204, 0.1) 0%, rgba(0, 102, 204, 0.05) 100%);
        border-left: 5px solid var(--primary);
        border-radius: 0.5rem;
        padding: 1rem;
    }
    
    /* Text input */
    .stTextArea textarea {
        background: white;
        border: 2px solid var(--border);
        border-radius: 0.5rem;
        color: var(--text-dark);
        font-size: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stTextArea textarea:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
    }
    
    /* File uploader */
    .stFileUploader {
        background: white;
        border: 2px solid var(--border);
        border-radius: 0.5rem;
        padding: 1rem;
    }
    
    /* Dataframe */
    .dataframe {
        border: 2px solid var(--border) !important;
        border-radius: 0.5rem !important;
    }
    
    /* Headers - DARK AND VISIBLE */
    h1, h2, h3 {
        color: var(--text-dark) !important;
        font-weight: 700 !important;
    }
    
    /* Subheader for "Example queries:" - MAKE IT DARK AND BOLD */
    .stMarkdown p strong {
        color: var(--text-dark) !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
    }
    
    /* Regular paragraphs */
    p {
        color: var(--text-gray);
        line-height: 1.6;
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

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
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
    
    st.markdown("#### 📊 System Stats")
    try:
        stats = st.session_state.vs_manager.get_collection_stats()
        cost_summary = st.session_state.rag_pipeline.get_cost_summary()
        
        st.metric("📚 Documents", stats.get("total_documents", 0))
        st.metric("🔍 Queries", cost_summary.get("query_count", 0))
        
        if show_costs:
            st.metric(
                "💰 Cost", 
                f"${cost_summary.get('total_cost', 0):.4f}",
                delta="100% FREE"
            )
    except Exception as e:
        st.warning("Stats loading...")
    
    st.divider()
    st.caption("🚀 LangChain • OpenRouter (FREE) • Streamlit")

# Main content
st.markdown('<div class="main-header">📊 Financial Earnings RAG System</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">🤖 AI-Powered Financial Document Analysis • 100% FREE • Lightning Fast ⚡</div>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["💬 Query", "📤 Upload", "📈 Analytics", "ℹ️ About"])

with tab1:
    st.markdown("### 🔍 Ask a Question")
    
    query = st.text_area(
        "Enter your question:",
        placeholder="e.g., What were Apple's Q3 2024 revenue drivers?",
        height=120
    )
    
    # FIXED: Make "Example queries:" label DARK and VISIBLE
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
            with st.spinner("🤔 Analyzing documents..."):
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
                    st.markdown(f"### 📚 Sources ({len(response['sources'])} documents)")
                    for idx, source in enumerate(response['sources'], 1):
                        with st.expander(f"📄 Source {idx}: {source['company']} - {source['quarter']} {source['year']}", expanded=idx==1):
                            st.markdown("**Content:**")
                            st.text(source['content'])
                            
                            if show_metadata:
                                c1, c2, c3 = st.columns(3)
                                c1.metric("Page", source['page'])
                                c2.metric("Quarter", source['quarter'])
                                c3.metric("Similarity", f"{source['similarity']:.3f}" if source['similarity'] else "N/A")
                
                if response.get('metrics'):
                    st.markdown("### 📊 Performance Metrics")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("⚡ Latency", f"{response.get('metrics', {}).get('latency', 0):.2f}s")
                    c2.metric("📄 Docs", response.get('metrics', {}).get('retrieved_docs', 0))
                    c3.metric("🔤 Tokens", f"{response.get('metrics', {}).get('total_tokens', 0):,}")
                    if show_costs:
                        c4.metric("💰 Cost", f"${response.get('metrics', {}).get('total_cost', 0):.6f}")
        else:
            st.warning("⚠️ Please enter a question")

with tab2:
    st.markdown("### 📤 Upload Documents")
    
    st.markdown("""
    <div class='upload-area'>
        <h3>📁 Drag and Drop Files Here</h3>
        <p style='color: #475569; font-weight: 500;'>Supported: PDF, DOCX • Max size: 200MB</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'docx'],
        help="Upload financial documents"
    )
    
    if uploaded_file:
        st.success(f"✅ File selected: **{uploaded_file.name}**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            doc_company = st.selectbox(
                "Company",
                ["Apple", "Microsoft", "Google", "Amazon", "Meta", "Tesla", "NVIDIA"],
                key="uc"
            )
        
        with col2:
            doc_year = st.number_input("Year", 2020, 2025, 2024, key="uy")
        
        with col3:
            doc_quarter = st.selectbox("Quarter", ["Q1", "Q2", "Q3", "Q4", "Annual"], key="uq")
        
        if st.button("🚀 Process & Upload", type="primary", use_container_width=True):
            with st.spinner("📄 Processing document..."):
                try:
                    temp_path = Path(f"/tmp/{uploaded_file.name}")
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    chunks = st.session_state.doc_processor.process_pdf(
                        pdf_path=str(temp_path),
                        metadata={
                            "company": doc_company,
                            "year": doc_year,
                            "quarter": doc_quarter,
                            "source": uploaded_file.name
                        }
                    )
                    
                    st.success(f"✅ Created {len(chunks)} chunks")
                    
                    with st.spinner("💾 Adding to database..."):
                        st.session_state.vs_manager.add_documents(chunks)
                    
                    stats = st.session_state.vs_manager.get_collection_stats()
                    st.success(f"🎉 Upload complete! Total documents: {stats['total_documents']}")
                    
                    temp_path.unlink()
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("📄 Chunks", len(chunks))
                    c2.metric("📚 Total Docs", stats['total_documents'])
                    c3.metric("✅ Status", "Ready")
                    
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    st.divider()
    st.markdown("### 📚 Current Database")
    try:
        stats = st.session_state.vs_manager.get_collection_stats()
        total = stats.get('total_documents', 0)
        if total > 0:
            st.info(f"📊 **{total}** documents in database")
        else:
            st.warning("📭 No documents yet - upload your first file above!")
    except:
        pass

with tab3:
    st.markdown("### 📈 Query Analytics")
    
    if st.session_state.query_history:
        history_df = pd.DataFrame([
            {
                "Time": h["timestamp"].strftime("%H:%M:%S"),
                "Query": h["query"][:40] + "..." if len(h["query"]) > 40 else h["query"],
                "Latency": f"{h['response'].get('metrics', {}).get('latency', 0):.2f}s",
                "Docs": h["response"].get("metrics", {}).get("retrieved_docs", 0),
                "Tokens": h["response"].get("metrics", {}).get("total_tokens", 0)
            }
            for h in st.session_state.query_history
        ])
        
        st.markdown("#### 📊 Summary")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🔍 Queries", len(st.session_state.query_history))
        c2.metric("⚡ Avg Latency", f"{history_df['Latency'].str.replace('s', '').astype(float).mean():.2f}s")
        c3.metric("💰 Total Cost", "$0.00")
        c4.metric("✅ Status", "FREE")
        
        st.markdown("#### 📋 History")
        st.dataframe(history_df, use_container_width=True, hide_index=True)
        
        if st.button("🗑️ Clear History"):
            st.session_state.query_history = []
            st.rerun()
    else:
        st.info("📭 No queries yet. Start in the Query tab!")

with tab4:
    st.markdown("### ℹ️ About This System")
    
    st.markdown("""
    **Financial RAG System** is a production-ready AI system for analyzing financial documents.
    
    #### ⚡ Key Features
    
    - 🤖 **Free LLM**: OpenRouter Llama 3.2 3B
    - 💾 **Local Embeddings**: sentence-transformers
    - 📤 **Easy Upload**: Drag & drop interface
    - ⚡ **Fast**: Sub-second response times
    - 💰 **100% FREE**: No API costs
    - 📊 **Analytics**: Track performance
    
    #### 🚀 How to Use
    
    1. **Upload** your financial PDFs in the Upload tab
    2. **Query** in natural language
    3. **Get** instant answers with citations
    4. **Analyze** performance metrics
    
    #### 📧 Contact
    
    Built by **Febin Varghese**  
    [GitHub Repository](https://github.com/fvcp94/financial-rag-system)
    """)

st.divider()
st.markdown("""
<div style='text-align: center; padding: 1rem;'>
    <p style='background: linear-gradient(135deg, #0066cc 0%, #7c3aed 100%); 
              -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
              font-weight: 800; font-size: 1.2rem;'>
        Financial RAG System v1.0.0
    </p>
    <p style='color: #475569; font-weight: 500;'>
        LangChain • OpenRouter (FREE) • Streamlit
    </p>
</div>
""", unsafe_allow_html=True)
