"""
Visualization Module

Functions for creating network visualizations (PNG, interactive, charts).
"""

import networkx as nx
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pyvis.network import Network
import tempfile
import os


def create_network_png(G, pagerank_scores, partition, output_path='network_viz.png', sample_size=500):
    """
    Create static network visualization as PNG.
    
    Args:
        G: NetworkX graph
        pagerank_scores: Dict of PageRank scores
        partition: Community partition dict
        output_path: Path to save PNG
        sample_size: Max nodes to visualize (for performance)
        
    Returns:
        str: Path to saved PNG file
    """
    # Sample graph if too large
    if G.number_of_nodes() > sample_size:
        # Get top nodes by PageRank
        top_nodes = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)[:sample_size]
        nodes_to_include = [node for node, _ in top_nodes]
        G_viz = G.subgraph(nodes_to_include).copy()
    else:
        G_viz = G
    
    # Create layout
    pos = nx.spring_layout(G_viz, seed=42, k=0.5, iterations=50)
    
    # Prepare node colors by community
    communities = {}
    for node in G_viz.nodes():
        comm = partition.get(node, 0)
        communities[node] = comm
    
    # Create color map
    unique_communities = set(communities.values())
    colors_map = plt.cm.tab20(range(len(unique_communities)))
    community_to_color = {comm: colors_map[i % len(colors_map)] for i, comm in enumerate(unique_communities)}
    
    node_colors = [community_to_color[communities[node]] for node in G_viz.nodes()]
    
    # Node sizes by PageRank
    node_sizes = [pagerank_scores.get(node, 0.001) * 5000 for node in G_viz.nodes()]
    
    # Separate positive and negative edges
    positive_edges = [(u, v) for u, v, d in G_viz.edges(data=True) if d.get('rating', 1) > 0]
    negative_edges = [(u, v) for u, v, d in G_viz.edges(data=True) if d.get('rating', 1) < 0]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(20, 15), facecolor='white')
    
    # Draw edges
    nx.draw_networkx_edges(G_viz, pos, edgelist=positive_edges, edge_color='#00ff88', 
                           alpha=0.3, width=0.5, ax=ax, arrows=False)
    nx.draw_networkx_edges(G_viz, pos, edgelist=negative_edges, edge_color='#ff4444',
                           alpha=0.3, width=0.5, ax=ax, arrows=False)
    
    # Draw nodes
    nx.draw_networkx_nodes(G_viz, pos, node_color=node_colors, node_size=node_sizes,
                           alpha=0.8, ax=ax)
    
    ax.set_title('Bitcoin OTC Trust Network', fontsize=24, fontweight='bold')
    ax.axis('off')
    
    # Add legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#00ff88', 
                   markersize=10, label='Positive Trust'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#ff4444',
                   markersize=10, label='Negative Distrust'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='gray',
                   markersize=15, label='High PageRank', alpha=0.7),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='gray',
                   markersize=5, label='Low PageRank', alpha=0.7)
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return output_path


def create_pyvis_interactive(G_trust, nodes_to_include, pagerank_scores, partition, 
                             width='100%', height='800px'):
    """
    Create interactive PyVis network visualization.
    
    Args:
        G_trust: Trust graph
        nodes_to_include: List of nodes to visualize
        pagerank_scores: PageRank scores dict
        partition: Community partition dict
        width: HTML width
        height: HTML height
        
    Returns:
        str: HTML content
    """
    import tempfile
    import os
    
    # Create PyVis network
    net = Network(width=width, height=height, bgcolor='#0a0a0a', font_color='#ffffff')
    net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=100)
    
    # Create subgraph
    subgraph = G_trust.subgraph(nodes_to_include)
    
    # Add nodes
    for node in subgraph.nodes():
        pr_score = pagerank_scores.get(node, 0)
        comm = partition.get(node, 0)
        
        size = 10 + pr_score * 5000
        colors = ['#00ff88', '#00ccff', '#ff00ff', '#ffaa00', '#ff4444']
        color = colors[comm % len(colors)]
        
        node_id = int(node)
        net.add_node(
            node_id,
            label=str(node_id),
            size=size,
            color=color,
            title=f"User {node_id}<br>PageRank: {pr_score:.6f}<br>Community: {comm}"
        )
    
    # Add edges
    for u, v, data in subgraph.edges(data=True):
        rating = data.get('rating', 1)
        edge_color = '#44ff88' if rating > 0 else '#ff4444'
        width = abs(rating) / 2
        
        net.add_edge(int(u), int(v), color=edge_color, width=width, title=f"Rating: {rating}")
    
    # Generate HTML
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as f:
        net.save_graph(f.name)
        with open(f.name, 'r') as f2:
            html = f2.read()
        os.unlink(f.name)
    
    return html


def plot_rating_distribution(df):
    """
    Create Plotly histogram of rating distribution.
    
    Args:
        df: DataFrame with 'rating' column
        
    Returns:
        plotly.graph_objects.Figure
    """
    rating_counts = df['rating'].value_counts().sort_index().reset_index()
    rating_counts.columns = ['Rating', 'Count']
    
    rating_counts['Color'] = rating_counts['Rating'].apply(
        lambda x: '#ff4444' if x < 0 else '#44ff88' if x > 0 else '#ffaa44'
    )
    
    fig = px.bar(
        rating_counts,
        x='Rating',
        y='Count',
        color='Color',
        color_discrete_map='identity',
        title='Rating Distribution: The J-Curve of Trust',
        labels={'Count': 'Frequency'},
        height=400
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e0e0e0', size=12),
        title_font=dict(size=18, color='#ffffff'),
        showlegend=False,
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)', type='log')
    )
    
    return fig


def plot_centrality_comparison(pagerank_df):
    """
    Create comparison chart for centrality metrics.
    
    Args:
        pagerank_df: DataFrame with centrality columns
        
    Returns:
        plotly.graph_objects.Figure
    """
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=pagerank_df['Node'].astype(str),
        y=pagerank_df['PageRank'],
        name='PageRank',
        marker_color='#00ff88'
    ))
    
    fig.update_layout(
        title='Top Nodes by PageRank',
        xaxis_title='Node ID',
        yaxis_title='PageRank Score',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff'),
        height=400
    )
    
    return fig


def plot_degree_distribution(G):
    """
    Plot degree distribution.
    
    Args:
        G: NetworkX graph
        
    Returns:
        plotly.graph_objects.Figure
    """
    degrees = [d for n, d in G.degree()]
    
    fig = px.histogram(
        x=degrees,
        nbins=50,
        title='Degree Distribution',
        labels={'x': 'Degree', 'y': 'Count'},
        color_discrete_sequence=['#00ccff']
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff'),
        height=350
    )
    
    return fig


def create_centrality_subgraph_viz(G_trust, pagerank_scores, top_n=20):
    """Create interactive visualization of top N nodes by centrality."""
    import tempfile, os
    from pyvis.network import Network
    
    # Get top N nodes
    top_nodes = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    top_node_ids = [n for n, _ in top_nodes]
    
    # Create subgraph
    subgraph = G_trust.subgraph(top_node_ids)
    
    # Create PyVis network
    net = Network(width='100%', height='600px', bgcolor='#0a0a0a', font_color='#ffffff')
    net.barnes_hut(gravity=-5000, central_gravity=0.3, spring_length=150)
    
    # Add nodes with gradient colors by rank
    for rank, (node, score) in enumerate(top_nodes, 1):
        # Color gradient: green to blue
        color_intensity = 1 - (rank / top_n)
        color = f'rgb({int(0*color_intensity)}, {int(255*color_intensity)}, {int(136 + 119*(1-color_intensity))})'
        
        size = 20 + score * 10000
        
        net.add_node(
            int(node),
            label=f"{node}\n#{rank}",
            size=size,
            color=color,
            title=f"Rank {rank}<br>PageRank: {score:.6f}"
        )
    
    # Add edges
    for u, v, data in subgraph.edges(data=True):
        net.add_edge(int(u), int(v), color='#44ff88', width=1)
    
    # Generate HTML
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as f:
        net.save_graph(f.name)
        with open(f.name, 'r') as f2:
            html = f2.read()
        os.unlink(f.name)
    
    return html


def create_community_viz(G_trust, partition, community_sizes, num_communities=2):
    """Visualize largest communities."""
    import tempfile, os
    from pyvis.network import Network
    
    # Get largest communities
    largest_comms = sorted(community_sizes.items(), key=lambda x: x[1], reverse=True)[:num_communities]
    comm_ids = [c for c, _ in largest_comms]
    
    # Get nodes in these communities
    nodes_to_show = [n for n, c in partition.items() if c in comm_ids]
    
    # Create subgraph
    subgraph = G_trust.subgraph(nodes_to_show)
    
    # Create PyVis
    net = Network(width='100%', height='600px', bgcolor='#0a0a0a', font_color='#ffffff')
    net.barnes_hut()
    
    # Color palette
    colors = ['#00ff88', '#00ccff', '#ff00ff', '#ffaa00', '#ff4444']
    
    # Add nodes
    for node in subgraph.nodes():
        comm = partition[node]
        color = colors[comm_ids.index(comm) % len(colors)]
        
        net.add_node(
            int(node),
            label=str(node),
            size=15,
            color=color,
            title=f"User {node}<br>Community {comm}<br>Size: {community_sizes[comm]}"
        )
    
    # Add edges
    for u, v in subgraph.edges():
        net.add_edge(int(u), int(v), color='rgba(255,255,255,0.2)', width=0.5)
    
    # Generate HTML
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as f:
        net.save_graph(f.name)
        with open(f.name, 'r') as f2:
            html = f2.read()
        os.unlink(f.name)
    
    return html


def create_path_viz(G_trust, path, pagerank_scores=None):
    """Visualize shortest path with highlighted edges."""
    import tempfile, os
    from pyvis.network import Network
    
    if not path or len(path) < 2:
        return "<p>No path to visualize</p>"
    
    # Get nodes within 1-hop of path for context
    context_nodes = set(path)
    for node in path:
        if node in G_trust:
            context_nodes.update(G_trust.neighbors(node))
    
    # Limit context to prevent huge graph
    if len(context_nodes) > 100:
        context_nodes = set(path)
    
    # Create subgraph
    subgraph = G_trust.subgraph(context_nodes)
    
    # Create PyVis
    net = Network(width='100%', height='600px', bgcolor='#0a0a0a', font_color='#ffffff')
    net.barnes_hut()
    
    # Path edges set
    path_edges = set((path[i], path[i+1]) for i in range(len(path)-1))
    
    # Add nodes
    for node in subgraph.nodes():
        if node in path:
            color = '#ff0000'  # Red for path nodes
            size = 25
        else:
            color = '#666666'  # Grey for context
            size = 10
        
        net.add_node(
            int(node),
            label=str(node),
            size=size,
            color=color,
            title=f"User {node}"
        )
    
    # Add edges
    for u, v in subgraph.edges():
        if (u, v) in path_edges or (v, u) in path_edges:
            net.add_edge(int(u), int(v), color='#ff0000', width=4)  # Red for path
        else:
            net.add_edge(int(u), int(v), color='rgba(255,255,255,0.1)', width=0.5)
    
    # Generate HTML
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as f:
        net.save_graph(f.name)
        with open(f.name, 'r') as f2:
            html = f2.read()
        os.unlink(f.name)
    
    return html


def create_component_viz(G, show_largest=True, show_smallest_n=0):
    """Visualize components (largest or smallest)."""
    import tempfile, os
    from pyvis.network import Network
    
    # Get components
    if G.is_directed():
        components = list(nx.weakly_connected_components(G))
    else:
        components = list(nx.connected_components(G))
    
    # Sort by size
    components.sort(key=len, reverse=True)
    
    # Select which to show
    if show_largest:
        nodes_to_show = list(components[0])
        title_text = f"Largest Component ({len(nodes_to_show)} nodes)"
    elif show_smallest_n > 0:
        nodes_to_show = []
        for comp in components[-show_smallest_n:]:
            nodes_to_show.extend(list(comp))
        title_text = f"Smallest {show_smallest_n} Components"
    else:
        nodes_to_show = list(components[0])
        title_text = "Component View"
    
    # Limit for performance
    if len(nodes_to_show) > 500:
        nodes_to_show = nodes_to_show[:500]
    
    # Create subgraph
    subgraph = G.subgraph(nodes_to_show)
    
    # Create PyVis
    net = Network(width='100%', height='600px', bgcolor='#0a0a0a', font_color='#ffffff')
    net.barnes_hut()
    
    # Add nodes
    for node in subgraph.nodes():
        net.add_node(
            int(node),
            label=str(node),
            size=12,
            color='#00ff88',
            title=f"User {node}"
        )
    
    # Add edges
    for u, v in subgraph.edges():
        net.add_edge(int(u), int(v), color='rgba(0,255,136,0.3)', width=0.5)
    
    # Generate HTML
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as f:
        net.save_graph(f.name)
        with open(f.name, 'r') as f2:
            html = f2.read()
        os.unlink(f.name)
    
    return html
