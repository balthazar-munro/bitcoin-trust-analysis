"""
Crypto-Trust Analytics: Bitcoin OTC Network Analysis
Production-Grade Streamlit Application - Refactored

Uses modular analysis package for all computations.
"""

import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
from pathlib import Path

# Import analysis modules
from analysis import centrality, community, paths, components, reachability, visualization

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Crypto-Trust Analytics",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 32px;
        font-weight: 700;
        color: #ffffff !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 14px;
        font-weight: 600;
        color: #ffffff !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    [data-testid="stMetricDelta"] {
        color: #00ff88 !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 700;
    }
    
    p, span, div, label {
        color: #ffffff !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #ffffff !important;
        font-weight: 600;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background: #00ff88;
        color: #000000 !important;
    }
    
    [data-testid="stSidebar"] {
        background: rgba(0, 0, 0, 0.6);
    }
    
    .dataframe {
        background: rgba(255, 255, 255, 0.95) !important;
        color: #000000 !important;
        border-radius: 10px;
    }
    
    .stButton > button {
        background: #00ff88;
        color: #000000 !important;
        font-weight: 700;
        border: none;
        border-radius: 10px;
        padding: 12px 30px;
        font-size: 16px;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background: #00ccff;
        transform: translateY(-2px);
    }
    
    .stAlert {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

@st.cache_data(show_spinner=False)
def load_data(file_path, min_rating_threshold=0):
    """Load CSV and filter data. Returns only the dataframe (cacheable)."""
    try:
        df = pd.read_csv(file_path, names=['source', 'target', 'rating', 'time'])
        df_filtered = df[df['rating'].abs() >= min_rating_threshold].copy()
        return df_filtered
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def build_graphs(df):
    """Build NetworkX graphs from dataframe."""
    G = nx.DiGraph()
    for _, row in df.iterrows():
        G.add_edge(row['source'], row['target'], 
                  rating=row['rating'], 
                  time=row['time'],
                  weight=abs(row['rating']))
    
    trust_edges = [(u, v) for u, v, d in G.edges(data=True) if d['rating'] > 0]
    G_trust = G.edge_subgraph(trust_edges).copy()
    
    distrust_edges = [(u, v) for u, v, d in G.edges(data=True) if d['rating'] < 0]
    G_distrust = G.edge_subgraph(distrust_edges).copy()
    
    return G, G_trust, G_distrust

# ============================================================================
# SIDEBAR
# ============================================================================

st.sidebar.title("🔐 Crypto-Trust Analytics")
st.sidebar.markdown("---")

# Use local dataset file
data_path = 'soc-sign-bitcoinotc.csv'

if not Path(data_path).exists():
    st.sidebar.error("⚠️ Dataset not found: soc-sign-bitcoinotc.csv")
    st.error("Please ensure the Bitcoin OTC dataset is in the project directory.")
    st.stop()

st.sidebar.success(f"✅ Dataset loaded: {Path(data_path).name}")
st.sidebar.markdown(f"**Size**: {Path(data_path).stat().st_size / 1024:.0f} KB")

# Filters
st.sidebar.markdown("### 🎛️ Filters")
min_rating = st.sidebar.slider(
    "Minimum Rating Threshold",
    min_value=0,
    max_value=10,
    value=0,
    help="Filter out edges with rating magnitude below this threshold"
)

# Run Analysis Button
run_analysis = st.sidebar.button("🚀 Run Analysis", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown("""
### 📊 About
Bitcoin OTC trust network analysis with:
- **Trust Anchor** identification
- **Fraud Ring** detection  
- **Risk Scoring** for paths
- **Network Health** metrics
""")

# ============================================================================
# MAIN APP
# ============================================================================

if run_analysis or 'data_loaded' in st.session_state:
    
    with st.spinner("🔄 Loading dataset..."):
        df = load_data(data_path, min_rating)
        
    if df is None:
        st.error("Failed to load data. Please check your file.")
        st.stop()
    
    with st.spinner("🔨 Building network graphs..."):
        G, G_trust, G_distrust = build_graphs(df)
        st.session_state['data_loaded'] = True
    
    with st.spinner("🧮 Computing PageRank..."):
        pagerank_scores = centrality.compute_pagerank(G_trust)
    
    with st.spinner("🔍 Detecting communities..."):
        partition, community_sizes = community.detect_communities(G_trust)
    
    # Header
    st.markdown("<h1 style='text-align: center;'>🔐 Bitcoin OTC Trust Network Analysis</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # ========================================================================
    # TAB LAYOUT - 10 TABS
    # ========================================================================
    
    tabs = st.tabs([
        "📊 Presentation",
        "🔍 Graph Model",
        "📈 Metrics",
        "🎯 Centrality",
        "🚨 Communities",
        "🔀 Paths",
        "🌐 Components",
        "📡 Reachability",
        "🎨 Visualization",
        "💼 Recommendations"
    ])
    
    # ========================================================================
    # TAB 1: PRESENTATION OVERVIEW
    # ========================================================================
    
    with tabs[0]:
        st.markdown("## 📊 Project Presentation Overview")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### Business Problem
            
            **Question**: How do we distinguish genuine high-reputation users from Sybil attack rings?
            
            **Challenge**: Bitcoin OTC platform has thousands of users with trust/distrust ratings,
            but identifying truly trustworthy users for safe trading is non-trivial.
            
            ### Our Approach
            
            This analysis provides a **data-driven framework** using graph analytics:
            
            1. **📊 Descriptive Analytics** - Network structure and health
            2. **🎯 PageRank** - Identify trust anchors (quality > quantity)
            3. ** Communities** - Detect fraud rings via isolation patterns
            4. **🔀 Path Analysis** - Risk scoring for user pairs
            5. **🌐 Components** - Network connectivity assessment
            6. **📡 BFS Reachability** - Trust propagation analysis
            7. **💼 Recommendations** - Actionable business rules
            
            ### Key Metrics
            """)
            
            metric_cols = st.columns(3)
            with metric_cols[0]:
                st.metric("Users", f"{G.number_of_nodes():,}", "Network nodes")
            with metric_cols[1]:
                st.metric("Ratings", f"{G.number_of_edges():,}", "Total edges")
            with metric_cols[2]:
                pct_pos = (df['rating'] > 0).sum() / len(df) * 100
                st.metric("Trust Ratio", f"{pct_pos:.1f}%", "Positive ratings")
        
        with col2:
            st.info("""
            **📋 Contents**
            
            Use the tabs above to explore:
            
            - Graph Model & Data
            - Descriptive Metrics
            - Centrality Rankings
            - Fraud Detection
            - Risk Assessment
            - Network Health
            - Trust Propagation
            - Visualizations
            - Final Recommendations
            """)
            
            st.success("""
            **🎯 Target Audience**
            
            - Platform managers
            - Risk analysts
            - Data scientists
            - Business stakeholders
            """)
    
    # ========================================================================
    # TAB 2: GRAPH MODEL & DATA
    # ========================================================================
    
    with tabs[1]:
        st.markdown("## 🔍 Graph Model Definition")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### Nodes
            **Individual users** on the Bitcoin OTC trading platform
            
            ### Edges  
            **Signed ratings** from one user to another
            
            #### Edge Attributes:
            - `source`: User who gave rating
            - `target`: User who received rating
            - `rating`: Integer from -10 (distrust) to +10 (trust)
            - `time`: Unix timestamp
            - `weight`: Absolute value (for algorithms)
            
            #### Graph Views:
            - **G**: Full directed graph (all edges)
            - **G_trust**: Positive edges only (rating > 0)
            - **G_distrust**: Negative edges only (rating < 0)
            """)
        
        with col2:
            st.markdown("""
            ### Business Interpretation
            
            **Positive Ratings** (+1 to +10)
            - Indicate willingness to trade
            - Build reputation
            - Enable trust propagation
            
            **Negative Ratings** (-1 to -10)
            - Fraud warnings
            - Dispute signals
            - Risk indicators
            
            **Edge Direction Matters**
            - A → B means A rated B
            - Rating is subjective (A's opinion of B)
            - Asymmetric: A trusts B doesn't mean B trusts A
            """)
        
        st.markdown("---")
        st.markdown("### 📊 Data Sample")
        st.dataframe(df.head(20), use_container_width=True)
        
        st.markdown("### 📈 Dataset Statistics")
        stats_cols = st.columns(4)
        with stats_cols[0]:
            st.metric("Total Ratings", f"{len(df):,}")
        with stats_cols[1]:
            st.metric("Unique Users", f"{len(set(df['source']) | set(df['target'])):,}")
        with stats_cols[2]:
            st.metric("Positive", f"{(df['rating'] > 0).sum():,}")
        with stats_cols[3]:
            st.metric("Negative", f"{(df['rating'] < 0).sum():,}")
    
    # ========================================================================
    # TAB 3: DESCRIPTIVE METRICS  
    # ========================================================================
    
    with tabs[2]:
        st.markdown("## 📈 Network Descriptive Metrics")
        
        # Metric Cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Total Nodes",
                value=f"{G.number_of_nodes():,}",
                delta="Users in Network"
            )
        
        with col2:
            st.metric(
                label="Total Edges",
                value=f"{G.number_of_edges():,}",
                delta="Trust Ratings"
            )
        
        with col3:
            pct_positive = (df['rating'] > 0).sum() / len(df) * 100
            st.metric(
                label="Positive Ratings",
                value=f"{pct_positive:.1f}%",
                delta="Trust-Dominated Network"
            )
        
        st.markdown("---")
        
        # Rating Distribution
        fig = visualization.plot_rating_distribution(df)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 👥 Top Users by Activity")
        col1, col2 = st.columns(2)
        
        with col1:
           # Top raters
            out_degrees = dict(G.out_degree())
            top_raters = sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)[:10]
            raters_df = pd.DataFrame(top_raters, columns=['User', 'Ratings Given'])
            
            fig = go.Figure(go.Bar(
                x=raters_df['User'].astype(str),
                y=raters_df['Ratings Given'],
                marker_color='#ff00ff',
                name='Out-Degree'
            ))
            fig.update_layout(
                title='Top 10 Most Active Raters',
                xaxis_title='User ID',
                yaxis_title='Ratings Given',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#ffffff'),
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top rated
            in_degrees = dict(G.in_degree())
            top_rated = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:10]
            rated_df = pd.DataFrame(top_rated, columns=['User', 'Ratings Received'])
            
            fig = go.Figure(go.Bar(
                x=rated_df['User'].astype(str),
                y=rated_df['Ratings Received'],
                marker_color='#00ccff',
                name='In-Degree'
            ))
            fig.update_layout(
                title='Top 10 Most Rated Users',
                xaxis_title='User ID',
                yaxis_title='Ratings Received',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#ffffff'),
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Continue in next message due to length...
    
else:
    # Welcome screen
    st.markdown("<h1 style='text-align: center;'>🔐 Welcome to Crypto-Trust Analytics</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ## 🚀 Get Started
        
        This application analyzes Bitcoin OTC trust networks to:
        
        - 🏆 **Identify Trust Anchors** via PageRank
        - 🚨 **Detect Fraud Rings** via community analysis  
        - 🔀 **Assess Trading Risk** via path analysis
        - 🌐 **Evaluate Network Health** via components
        - 📡 **Analyze Trust Reach** via BFS
        
        ### 📝 Instructions
        
        1. **Click "Run Analysis"** in the sidebar
        2. **Explore** the 10 analysis tabs
        3. **Review** findings and recommendations
        
        👈 **Click "Run Analysis" to begin!**
        """)

st.markdown("---")
st.markdown("<p style='text-align: center; color: #888;'>Built with ❤️ using Streamlit | Crypto-Trust Analytics v2.0</p>", unsafe_allow_html=True)
