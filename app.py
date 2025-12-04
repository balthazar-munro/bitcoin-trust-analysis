"""
Crypto-Trust Analytics: Bitcoin OTC Network Analysis
Complete Enhanced Application with Graph Visualizations

Version: 3.0 (Enhanced Visualizations with Proper Clustering, Color Coding, Sizing, and Labels)
- Fixed tab indexing bugs
- Improved node size scaling for better visibility
- Added proper color coding for communities, paths, and components
- Limited node counts for readable visualizations
- Added interactive controls for customizing visualizations
- Added reachability visualization
- Added suspicious community visualization
"""

import streamlit as st
import pandas as pd
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
# CUSTOM CSS - FIXED
# ============================================================================

st.markdown("""
<style>
    /* Remove white header bar */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%) !important;
    }
    
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    /* Fix dropdown/selectbox text color - make it black for readability */
    .stSelectbox [data-baseweb="select"],
    .stSelectbox [data-baseweb="select"] * {
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #000000 !important;
    }

    .stSelectbox [data-baseweb="select"] > div,
    .stSelectbox [data-baseweb="select"] > div > div {
        color: #000000 !important;
        background-color: rgba(255, 255, 255, 0.95) !important;
    }

    .stSelectbox option,
    [data-baseweb="menu"] *,
    [data-baseweb="popover"] * {
        color: #000000 !important;
        background-color: #ffffff !important;
    }

    /* Fix multiselect */
    .stMultiSelect [data-baseweb="select"] *,
    .stMultiSelect [data-baseweb="tag"] * {
        color: #000000 !important;
    }

    /* Fix text input */
    .stTextInput input,
    .stNumberInput input {
        color: #000000 !important;
        background-color: rgba(255, 255, 255, 0.95) !important;
    }

    /* Fix slider labels */
    .stSlider [data-baseweb="slider"] {
        color: #ffffff !important;
    }

    /* Fix radio buttons text */
    .stRadio label span {
        color: #ffffff !important;
    }

    /* Fix expander content text on white background */
    .streamlit-expanderContent {
        color: #ffffff !important;
    }

    /* Ensure info/warning/error boxes have black text */
    .stAlert > div {
        color: #000000 !important;
    }

    .stAlert p, .stAlert span, .stAlert div {
        color: #000000 !important;
    }
    
    /* Metrics */
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
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    
    p, span, div, label {
        color: #ffffff !important;
    }
    
    /* Improved spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Tabs */
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
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(0, 0, 0, 0.6);
    }
    
    /* DataFrames */
    .dataframe {
        background: rgba(255, 255, 255, 0.95) !important;
        color: #000000 !important;
        border-radius: 10px;
    }
    
    /* Buttons */
    .stButton > button {
        background: #00ff88;
        color: #000000 !important;
        font-weight: 700;
        border: none;
        border-radius: 10px;
        padding: 12px 30px;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background: #00ccff;
        transform: translateY(-2px);
    }
    
    /* Alerts */
    .stAlert {
        color: #000000 !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data(show_spinner=False)
def load_data(file_path, min_rating_threshold=0):
    """Load and filter CSV data."""
    try:
        df = pd.read_csv(file_path, names=['source', 'target', 'rating', 'time'])
        return df[df['rating'].abs() >= min_rating_threshold].copy()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def build_graphs(df):
    """Build NetworkX graphs from dataframe."""
    G = nx.DiGraph()
    for _, row in df.iterrows():
        G.add_edge(row['source'], row['target'], rating=row['rating'], time=row['time'], weight=abs(row['rating']))
    
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

data_path = 'soc-sign-bitcoinotc.csv'
if not Path(data_path).exists():
    st.sidebar.error("⚠️ Dataset not found")
    st.stop()

st.sidebar.success(f"✅ Dataset: {Path(data_path).name}")
st.sidebar.markdown(f"**Size**: {Path(data_path).stat().st_size / 1024:.0f} KB")

st.sidebar.markdown("### 🎛️ Filters")
min_rating = st.sidebar.slider("Minimum Rating Threshold", 0, 10, 0)

run_analysis = st.sidebar.button("🚀 Run Analysis", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown("""
### 📊 About
Bitcoin OTC trust network analysis with:
- Trust Anchor identification (PageRank)
- Fraud Ring detection (Communities)
- Risk Scoring (Path Analysis)
- Network Health (Components)
""")

# ============================================================================
# MAIN APP
# ============================================================================

if run_analysis or 'data_loaded' in st.session_state:
    
    # Load data
    with st.spinner("🔄 Loading data..."):
        df = load_data(data_path, min_rating)
        if df is None:
            st.stop()
        G, G_trust, G_distrust = build_graphs(df)
        st.session_state['data_loaded'] = True
    
    # Compute analytics
    with st.spinner("🧮 Computing analytics..."):
        pagerank_scores = centrality.compute_pagerank(G_trust)
        partition, community_sizes = community.detect_communities(G_trust)
        comp_stats = components.analyze_components(G)
        connectivity = components.analyze_component_connectivity(G)
        suspicious = community.find_suspicious_communities(G_trust, partition, community_sizes, max_size=10)
    
    st.markdown("<h1 style='text-align: center;'>🔐 Bitcoin OTC Trust Network Analysis</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # ========================================================================
    # 10 TABS WITH VISUALIZATIONS
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
    # TAB 1: PRESENTATION
    # ========================================================================
    
    with tabs[0]:
        st.markdown("## 📊 Presentation Overview")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### Business Problem
            **How to distinguish genuine users from Sybil attack rings?**
            
            In cryptocurrency trading platforms, trust is paramount. However, malicious actors can:
            - Create fake "sock puppet" accounts
            - Rate each other highly to appear trustworthy
            - Scam legitimate users once "trusted"
            
            ### Our Data-Driven Solution
            
            Using graph analytics, we can detect these patterns:
            
            1. **📊 Network Structure Analysis** - Understand overall health
            2. **🎯 PageRank Algorithm** - Quality over quantity in trust
            3. **🚨 Community Detection** - Identify isolated fraud rings
            4. **🔀 Path Analysis** - Score transaction risk
            5. **🌐 Component Analysis** - Network fragmentation
            6. **📡 Trust Propagation** - How trust spreads
            
            **Result**: Automated, scalable fraud detection and risk scoring.
            """)
            
            cols = st.columns(3)
            with cols[0]:
                st.metric("Users", f"{G.number_of_nodes():,}", "Network nodes")
            with cols[1]:
                st.metric("Ratings", f"{G.number_of_edges():,}", "Trust edges")
            with cols[2]:
                pct_pos = (df['rating'] > 0).sum() / len(df) * 100
                st.metric("Trust %", f"{pct_pos:.1f}%", "Positive ratings")
        
        with col2:
            st.info("""
            **📋 Navigate Through Tabs**
            
            - **Graph Model**: Data structure
            - **Metrics**: Descriptive stats
            - **Centrality**: Trust anchors
            - **Communities**: Fraud detection
            - **Paths**: Risk assessment
            - **Components**: Network health
            - **Reachability**: Trust reach
            - **Visualization**: Network views
            - **Recommendations**: Actions
            """)
            
            st.success("""
            **🎯 For Stakeholders**
            
            - Platform managers
            - Risk analysts
            - Compliance teams
            - ML engineers
            """)
    
    # ========================================================================
    # TAB 2: GRAPH MODEL
    # ========================================================================

    with tabs[1]:
        st.markdown("## 🔍 Graph Model Definition")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### Graph Structure
            
            **Nodes**: Individual Bitcoin OTC users  
            **Edges**: Signed ratings between users
            
            #### Edge Attributes
            - `source`: Rater (who gave the rating)
            - `target`: Ratee (who received it)
            - `rating`: -10 (total distrust) to +10 (total trust)
            - `time`: Unix timestamp
            - `weight`: abs(rating) for algorithms
            
            #### Three Graph Views
            - **G**: Full network (all ratings)
            - **G_trust**: Positive edges only
            - **G_distrust**: Negative edges only
            
            **Why Directed?** A trusts B ≠ B trusts A
            """)
        
        with col2:
            st.markdown("""
            ### Business Interpretation
            
            **Positive Ratings** (+1 to +10)
            - ✅ Successful past trades
            - ✅ Willingness to transact again
            - ✅ Builds platform reputation
            
            **Negative Ratings** (-1 to -10)
            - ⚠️ Disputed transactions
            - ⚠️ Suspected fraud
            - ⚠️ Warning to other users
            
            **The "J-Curve"**
            - Most ratings are +10 (very positive)
            - Few moderate ratings (polarized)
            - Very few negative ratings
            - indicates high-quality platform!
            """)
        
        st.markdown("---")
        st.markdown("### 📊 Data Sample")
        st.dataframe(df.head(20), use_container_width=True)
        
        st.markdown("### 📈 Dataset Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Ratings", f"{len(df):,}")
        with col2:
            st.metric("Unique Users", f"{len(set(df['source']) | set(df['target'])):,}")
        with col3:
            st.metric("Positive", f"{(df['rating'] > 0).sum():,}")
        with col4:
            st.metric("Negative", f"{(df['rating'] < 0).sum():,}")
    
    # ========================================================================
    # TAB 3: METRICS
    # ========================================================================
    
    with tabs[2]:
        st.markdown("## 📈 Descriptive Network Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Nodes", f"{G.number_of_nodes():,}", "Users")
        with col2:
            st.metric("Total Edges", f"{G.number_of_edges():,}", "Ratings")
        with col3:
            pct_positive = (df['rating'] > 0).sum() / len(df) * 100
            st.metric("Positive %", f"{pct_positive:.1f}%", "Trust-dominated")
        
        st.markdown("---")
        
        # Rating distribution
        fig = visualization.plot_rating_distribution(df)
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("💡 Why the J-Curve Matters"):
            st.markdown("""
            The **J-shaped distribution** indicates a healthy reputation system:
            - High concentration at +10 = users rewarding good behavior
            - Low middle ratings = clear signal (not noise)
            - Few negative ratings = effective deterrent or low fraud
            
            **Business Impact**: Most of platform activity is legitimate.
            """)
    
    # ========================================================================
    # TAB 4: CENTRALITY + VISUALIZATION
    # ========================================================================
    
    with tabs[3]:
        st.markdown("## 🎯 Trust Anchor Identification (PageRank)")
        
        with st.expander("📖 What is PageRank in Trust Networks?"):
            st.markdown("""
            **PageRank** measures influence based on *who* trusts you, not just *how many*.
            
            **Key Insight**: Being trusted by other high-trust users is more valuable than many ratings from unknown users.
            
            **Use Case**: Identify genuine community leaders vs. self-promotion rings.
            
            **Formula**: Iterative algorithm where each node's score depends on scores of nodes linking to it.
            """)
        
        # Leaderboard
        top_pr = centrality.get_top_nodes(pagerank_scores, n=20)
        pr_df = pd.DataFrame([
            (i+1, u, f"{s:.6f}", G_trust.in_degree(u)) 
            for i, (u, s) in enumerate(top_pr)
        ], columns=['Rank', 'User ID', 'PageRank Score', 'In-Degree'])
        
        st.markdown("### 🏆 Top 20 Trust Anchors")
        st.dataframe(pr_df, use_container_width=True, height=400)
        
        # Visualization
        st.markdown("### 📊 Trust Anchor Network Visualization")
        st.markdown("**Top 20 nodes with connections between them**")
        
        if st.button("🎨 Generate Centrality Graph"):
            with st.spinner("Creating visualization..."):
                html = visualization.create_centrality_subgraph_viz(G_trust, pagerank_scores, top_n=20)
                st.components.v1.html(html, height=650, scrolling=False)

                st.info("""
                **Legend**:
                - **Node size** = Rank position (larger = higher ranked)
                - **Green nodes (#1-7)** = Top tier trust anchors
                - **Cyan nodes (#8-14)** = Mid tier influencers
                - **Blue nodes (#15-20)** = Lower tier but still top 20
                - **Edges** = Trust connections between top users
                - **Hover** = View detailed PageRank score
                """)
    
    # ========================================================================
    # TAB 5: COMMUNITIES + VISUALIZATION
    # ========================================================================
    
    with tabs[4]:
        st.markdown("## 🚨 Community Detection & Fraud Rings")
        
        with st.expander("📖 Why Community Detection Detects Fraud"):
            st.markdown("""
            **Sybil Attack Pattern**:
            1. Attacker creates multiple fake accounts
            2. Accounts rate each other highly
            3. Cluster forms with NO external connections
            4. Appears "trusted" but is completely isolated
            
            **Detection Heuristic**:
            - Small size (< 10-15 users)
            - Dense internal connections
            - Zero connections to main network
            
            **Algorithm**: Louvain modularity optimization
            """)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Communities", len(community_sizes))
        with col2:
            st.metric("Largest Community", max(community_sizes.values()) if community_sizes else 0)
        with col3:
            st.metric("Suspicious Clusters", len(suspicious))
        
        if suspicious:
            st.warning("### ⚠️ Flagged for Review")
            fraud_df = pd.DataFrame(suspicious)
            fraud_df['Users'] = fraud_df['Users'].apply(lambda x: ', '.join(map(str, x[:5])) + ('...' if len(x) > 5 else ''))
            st.dataframe(fraud_df, use_container_width=True)
            
            st.error("""
            **Recommended Action**: Manual security review required for these users before allowing large transactions.
            """)
        else:
            st.success("✅ No suspicious isolated communities detected")
        
        # Community Visualization
        st.markdown("### 📊 Community Structure Visualization")

        col1, col2 = st.columns(2)
        with col1:
            num_comms = st.slider("Number of communities to show", 2, 5, 3, key='num_comms')
        with col2:
            nodes_per_comm = st.slider("Max nodes per community", 15, 50, 30, key='nodes_per_comm')

        if st.button("🎨 Generate Community Graph"):
            with st.spinner("Creating visualization..."):
                html = visualization.create_community_viz(
                    G_trust, partition, community_sizes,
                    num_communities=num_comms,
                    max_nodes_per_community=nodes_per_comm
                )
                st.components.v1.html(html, height=650, scrolling=False)

                st.info("""
                **Legend**:
                - Each color = different community
                - Node size = uniform for clarity
                - Red edges = inter-community connections (bridges)
                - White edges = intra-community connections
                """)

        # Suspicious communities visualization
        if suspicious:
            st.markdown("### 🚨 Suspicious Communities Visualization")
            if st.button("🎨 Visualize Suspicious Clusters"):
                with st.spinner("Creating visualization..."):
                    html = visualization.create_suspicious_community_viz(
                        G_trust, suspicious, partition, max_display=5
                    )
                    st.components.v1.html(html, height=650, scrolling=False)
                    st.warning("**Red nodes** = First suspicious community. Other colors = additional suspicious clusters.")
    
    # ========================================================================
    # TAB 6: PATHS + VISUALIZATION
    # ========================================================================
    
    with tabs[5]:
        st.markdown("## 🔀 Trust Path Finder & Risk Scoring")
        
        with st.expander("📖 Why Path Length Matters for Risk"):
            st.markdown("""
            **Trust Transitivity**: If A trusts B and B trusts C, then A might trust C (to some degree).
            
            **Path Length = Degrees of Separation**:
            - 1-2 hops: Direct or very close connection → LOW RISK
            - 3-4 hops: Extended network → MEDIUM RISK
            - 5+ hops or no path: No trust chain → HIGH RISK
            
            **Business Use**: Pre-transaction risk assessment.
            """)
        
        trust_users = sorted(list(G_trust.nodes()))[:200]  # Limit for dropdown performance
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            source = st.selectbox("Source User", trust_users, index=0, key='path_source')
        with col2:
            target = st.selectbox("Target User", trust_users, index=min(1, len(trust_users)-1), key='path_target')
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            find_btn = st.button("🔍 Find Path", use_container_width=True)
        
        # Store path in session state to persist across button clicks
        if find_btn and source and target:
            path_info = paths.find_shortest_path(G_trust, source, target)
            st.session_state['current_path_info'] = path_info
            st.session_state['current_path_source'] = source
            st.session_state['current_path_target'] = target

        # Display path info if available in session state
        if 'current_path_info' in st.session_state:
            path_info = st.session_state['current_path_info']

            if path_info['exists']:
                st.success(f"✅ Path exists: **{path_info['length']} hops** (from {st.session_state.get('current_path_source')} to {st.session_state.get('current_path_target')})")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Path Length", f"{path_info['length']} hops")
                with col2:
                    st.metric("Avg Trust", f"{path_info['average_trust']:.2f}/10")
                with col3:
                    risk = paths.assess_path_risk(path_info)
                    risk_color = {"LOW": "🟢", "MEDIUM": "🟡", "ELEVATED": "🟠", "HIGH": "🔴"}
                    st.metric("Risk Level", f"{risk_color.get(risk, '⚪')} {risk}")

                st.markdown(f"**Path**: {' → '.join(map(str, path_info['path']))}")

                # Interpretation
                if path_info['length'] <= 2:
                    st.info("**Interpretation**: Direct connection. Transaction safe to proceed.")
                elif path_info['length'] <= 4:
                    st.warning("**Interpretation**: Extended trust path. Consider transaction limits.")
                else:
                    st.error("**Interpretation**: Distant connection. Require additional verification.")

                # Path Visualization
                st.markdown("### 📊 Path Visualization")
                if st.button("🎨 Visualize Path"):
                    with st.spinner("Creating visualization..."):
                        html = visualization.create_path_viz(G_trust, path_info['path'])
                        st.components.v1.html(html, height=650, scrolling=False)

                        st.info("""
                        **Legend**:
                        - **Green node** = Source (START)
                        - **Yellow nodes** = Path steps
                        - **Red node** = Target (END)
                        - **Yellow edges** = Trust path
                        - **Grey** = Context nodes for reference
                        """)
            else:
                st.error(f"❌ No path exists: {path_info['error']}")
                st.warning("**Interpretation**: No trust relationship. HIGH RISK - do not proceed without verification.")
    
    # ========================================================================
    # TAB 7: COMPONENTS + VISUALIZATION
    # ========================================================================
    
    with tabs[6]:
        st.markdown("## 🌐 Network Components & Health Analysis")
        
        with st.expander("📖 Why Component Analysis Matters"):
            st.markdown("""
            **Weakly Connected Components** = groups of nodes where paths exist (ignoring edge direction).
            
            **Network Health Indicators**:
            - **1 large component**: Well-connected platform
            - **Many components**: Fragmented, isolated user groups
            - **Isolated nodes**: New users or inactive accounts
            
            **Business Impact**: High fragmentation → trust can't propagate → higher risk
            """)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Components", comp_stats['num_components'])
        with col2:
            st.metric("Largest Size", f"{comp_stats['largest_component_size']:,}")
        with col3:
            st.metric("Coverage", f"{comp_stats['largest_component_pct']:.1f}%")
        
        # Health assessment
        health_emoji = {"EXCELLENT": "🟢", "GOOD": "🟡", "MODERATE": "🟠", "FRAGMENTED": "🔴"}
        st.markdown(f"### Network Health: {health_emoji.get(connectivity['health'], '⚪')} **{connectivity['health']}**")
        
        if connectivity['health'] in ['EXCELLENT', 'GOOD']:
            st.success("Network is well-connected. Trust can propagate effectively across the platform.")
        else:
            st.warning("Network shows fragmentation. Some users may be isolated from the main community.")
        
        # Component Visualization
        st.markdown("### 📊 Component Visualization")

        col1, col2 = st.columns(2)
        with col1:
            viz_choice = st.radio("Show:", ["Largest Component", "5 Smallest Components"])
        with col2:
            max_nodes_comp = st.slider("Max nodes to display", 50, 150, 100, key='max_nodes_comp')

        if st.button("🎨 Generate Component Graph"):
            with st.spinner("Creating visualization..."):
                if viz_choice == "Largest Component":
                    html = visualization.create_component_viz(G, show_largest=True, max_nodes=max_nodes_comp)
                else:
                    html = visualization.create_component_viz(G, show_largest=False, show_smallest_n=5, max_nodes=max_nodes_comp)

                st.components.v1.html(html, height=650, scrolling=False)

                st.info(f"""
                **Showing**: {viz_choice}
                - **Green nodes** = Users in component
                - **Green edges** = Trust ratings
                - **Red edges** = Distrust ratings
                - Nodes sampled by degree (most connected shown)
                """)
    
    # ========================================================================
    # TAB 8: REACHABILITY (BFS)
    # ========================================================================
    
    with tabs[7]:
        st.markdown("## 📡 Trust Reachability Analysis (BFS)")
        
        with st.expander("📖 Understanding Trust Propagation"):
            st.markdown("""
            **BFS (Breadth-First Search)** explores the network layer by layer:
            - **1-hop**: Direct connections
            - **2-hop**: Friends of friends
            - **3-hop**: Extended network
            
            **Trust Radius** = how many users a trust anchor can influence.
            
            **Business Value**: Measure impact of onboarding high-trust users.
            """)
        
        top_anchors = [u for u, _ in centrality.get_top_nodes(pagerank_scores, n=5)]
        
        st.markdown("### Trust Radius of Top Anchors")
        
        for user in top_anchors[:3]:
            radius = reachability.compute_trust_radius(G_trust, user, max_hops=3)
            
            with st.expander(f"User {user} - Trust Radius"):
                cols = st.columns(3)
                with cols[0]:
                    st.metric("1-hop reach", f"{radius['reachable_at_hop'][1]:,}", "Direct connections")
                with cols[1]:
                    st.metric("2-hop reach", f"{radius['cumulative'][2]:,}", "Cumulative")
                with cols[2]:
                    st.metric("3-hop total", f"{radius['total_reachable']:,}", "Full reach")
        
        st.info("""
        💡 **Business Insight**: Top trust anchors can reach thousands of users within 2-3 hops.
        Prioritize these users for platform governance and dispute resolution.
        """)

        # Reachability Visualization
        st.markdown("### 📊 Trust Radius Visualization")
        st.markdown("See how trust propagates from a selected anchor user")

        selected_anchor = st.selectbox(
            "Select a trust anchor to visualize reach",
            top_anchors[:5],
            format_func=lambda x: f"User {x} (#{top_anchors.index(x)+1})",
            key='reach_viz_anchor'
        )

        if st.button("🎨 Visualize Trust Radius"):
            with st.spinner("Creating visualization..."):
                radius = reachability.compute_trust_radius(G_trust, selected_anchor, max_hops=3)
                html = visualization.create_reachability_viz(G_trust, selected_anchor, radius)
                st.components.v1.html(html, height=650, scrolling=False)

                st.info("""
                **Legend**:
                - **Red (center)** = Source anchor user
                - **Green** = 1-hop (direct connections)
                - **Cyan** = 2-hop (friends of friends)
                - **Purple** = 3-hop (extended network)
                """)
    
    # ========================================================================
    # TAB 9: VISUALIZATION GALLERY
    # ========================================================================
    
    with tabs[8]:
        st.markdown("## 🎨 Network Visualization Gallery")
        
        st.info("Generate various network visualizations to explore the trust network structure.")
        
        viz_type = st.selectbox(
            "Choose Visualization Type",
            ["Interactive Full Network (PyVis)", "Static PNG Export"],
            key='viz_type_select'
        )
        
        if viz_type == "Interactive Full Network (PyVis)":
            st.markdown("### Interactive Network (Top Nodes by PageRank)")

            num_nodes_viz = st.slider("Number of nodes to visualize", 30, 100, 60, key='num_nodes_viz')

            if st.button("🎨 Generate Interactive Graph", key='gen_pyvis'):
                with st.spinner("Creating visualization..."):
                    top_nodes = [u for u, _ in centrality.get_top_nodes(pagerank_scores, n=num_nodes_viz)]
                    html = visualization.create_pyvis_interactive(
                        G_trust, top_nodes, pagerank_scores, partition
                    )
                    st.components.v1.html(html, height=700, scrolling=True)

                    st.info("""
                    **How to use**:
                    - **Drag** nodes to rearrange
                    - **Zoom** with mouse wheel
                    - **Hover** for user details
                    - **Node size** = PageRank score (bigger = more influential)
                    - **Node color** = Community membership
                    - **Edge color**: Green = trust, Red = distrust
                    - **Labels** show rank for top 20 users
                    """)
        else:
            st.markdown("### Static PNG Export")
            
            if st.button("🎨 Generate PNG", key='gen_png'):
                with st.spinner("Creating PNG..."):
                    png_path = visualization.create_network_png(
                        G_trust, pagerank_scores, partition,
                        output_path='network_visualization.png',
                        sample_size=300
                    )
                    st.success(f"✅ Saved to: {png_path}")
                    st.info("PNG file created in project directory. Use for presentations.")
    
    # ========================================================================
    # TAB 10: RECOMMENDATIONS
    # ========================================================================
    
    with tabs[9]:
        st.markdown("## 💼 Business Recommendations & Implementation")
        
        st.markdown(f"""
        ### 📊 Executive Summary
        
        **Network Status**: {connectivity['health']} ({comp_stats['largest_component_pct']:.1f}% connected)  
        **Trust Anchors**: {len([s for s in pagerank_scores.values() if s > 0.001])} identified  
        **Fraud Flags**: {len(suspicious)} suspicious communities  
        **Platform Health**: {pct_positive:.1f}% positive ratings
        
        ---
        
        ### 🎯 Recommended Actions
        
        #### 1. Implement Trust Tier System
        
        **Tier Structure**:
        - 🥇 **GOLD**: Top 20 PageRank users (verified trust anchors)
        - 🥈 **SILVER**: Within 2 hops of GOLD users
        - 🥉 **BRONZE**: Within 3 hops of GOLD users
        - ⚪ **UNVERIFIED**: All others
        
        **Business Rules**:
        - GOLD: Unlimited trading, governance voting rights
        - SILVER: Standard limits, trusted by proximity
        - BRONZE: Reduced limits, monitored transactions
        - UNVERIFIED: Require ID verification for large trades
        
        #### 2. Automated Fraud Detection Pipeline
        
        **Daily Job**:
        1. Run community detection
        2. Flag clusters with <15 nodes + zero external links
        3. Alert security team for manual review
        4. Temporarily restrict flagged accounts
        
        **Expected Impact**: Catch 80%+ of Sybil attacks before damage
        
        #### 3. Pre-Transaction Risk Scoring
        
        **For each transaction request**:
        ```python
        risk_score = assess_path_risk(source, target)
        
        if risk_score == "LOW":
            approve_immediately()
        elif risk_score == "MEDIUM":
            set_transaction_limit(1000)
        else:  # HIGH
            require_additional_verification()
        ```
        
        #### 4. Trust Propagation Strategy
        
        - **Recruit high-PageRank users** as platform ambassadors
        - **Incentivize** GOLD users with reduced fees
        - **Bootstrap new markets** by seeding with trust anchors
        
        ---
        
        ### 📈 Success Metrics (Track Monthly)
        
        | Metric | Current | Target (6mo) |
        |--------|---------|--------------|
        | % Network Coverage | {comp_stats['largest_component_pct']:.1f}% | >95% |
        | Fraud Detection Rate | TBD | >80% |
        | False Positive Rate | TBD | <5% |
        | Avg Transaction Risk | TBD | <MEDIUM |
        | GOLD User Count | 20 | 50 |
        
        ---
        
        ### 🚀 Implementation Roadmap
        
        **Phase 1 (Month 1-2)**: Foundation
        - Deploy analysis as daily batch job
        - Build trust tier assignment system
        - Create internal fraud alert dashboard
        
        **Phase 2 (Month 3-4)**: Integration
        - Integrate risk scores into transaction API
        - Launch GOLD/SILVER/BRONZE badges
        - Begin A/B testing tier-based limits
        
        **Phase 3 (Month 5-6)**: Optimization
        - Real-time risk scoring (sub-second latency)
        - ML-enhanced fraud detection
        - User-facing trust path visualization
        
        ---
        
        ### ✅ Next Steps
        
        1. **Get stakeholder approval** for trust tier design
        2. **Run production pilot** on 10% of users
        3. **Measure impact** on fraud rate and user experience
        4. **Iterate and scale**
        
        **Status**: Analysis complete, ready for production deployment 🚀
        """)

else:
    # ====================================================================
    # WELCOME SCREEN
    # ====================================================================
    
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
        
        1. Click **"Run Analysis"** in the sidebar
        2. Explore the **10 analysis tabs**
        3. Review **findings and recommendations**
        
        👈 **Click "Run Analysis" to begin!**
        """)

st.markdown("---")
st.markdown("<p style='text-align: center; color: #888;'>Crypto-Trust Analytics v3.0 | Enhanced Visualizations with Proper Clustering & Color Coding</p>", unsafe_allow_html=True)
