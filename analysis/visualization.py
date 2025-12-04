"""
Visualization Module

Functions for creating network visualizations (PNG, interactive, charts).
Enhanced with better readability, proper scaling, clustering, and color coding.
"""

import networkx as nx
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pyvis.network import Network
import tempfile
import os
import random


# Color palettes for consistent styling
COMMUNITY_COLORS = [
    '#00ff88',  # Green
    '#00ccff',  # Cyan
    '#ff6b6b',  # Coral
    '#ffd93d',  # Yellow
    '#c44dff',  # Purple
    '#ff8c42',  # Orange
    '#6bcb77',  # Light green
    '#4d96ff',  # Blue
    '#ff6b9d',  # Pink
    '#98d8c8',  # Teal
]

RISK_COLORS = {
    'LOW': '#00ff88',
    'MEDIUM': '#ffd93d',
    'ELEVATED': '#ff8c42',
    'HIGH': '#ff4444'
}


def create_network_png(G, pagerank_scores, partition, output_path='network_viz.png', sample_size=300):
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
    # Sample graph if too large - prioritize high PageRank nodes
    if G.number_of_nodes() > sample_size:
        top_nodes = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)[:sample_size]
        nodes_to_include = [node for node, _ in top_nodes]
        G_viz = G.subgraph(nodes_to_include).copy()
    else:
        G_viz = G

    # Create layout with better spacing
    pos = nx.spring_layout(G_viz, seed=42, k=1.5/((G_viz.number_of_nodes())**0.5), iterations=50)

    # Prepare node colors by community
    unique_communities = set(partition.get(node, 0) for node in G_viz.nodes())
    community_to_color = {comm: COMMUNITY_COLORS[i % len(COMMUNITY_COLORS)]
                          for i, comm in enumerate(sorted(unique_communities))}
    node_colors = [community_to_color[partition.get(node, 0)] for node in G_viz.nodes()]

    # Node sizes by PageRank with better scaling
    pr_values = [pagerank_scores.get(node, 0.0001) for node in G_viz.nodes()]
    max_pr = max(pr_values) if pr_values else 1
    min_pr = min(pr_values) if pr_values else 0
    # Scale between 50 and 500
    node_sizes = [50 + 450 * ((pr - min_pr) / (max_pr - min_pr + 0.0001)) for pr in pr_values]

    # Separate positive and negative edges
    positive_edges = [(u, v) for u, v, d in G_viz.edges(data=True) if d.get('rating', 1) > 0]
    negative_edges = [(u, v) for u, v, d in G_viz.edges(data=True) if d.get('rating', 1) < 0]

    # Create figure
    fig, ax = plt.subplots(figsize=(16, 12), facecolor='#1a1a2e')
    ax.set_facecolor('#1a1a2e')

    # Draw edges
    if positive_edges:
        nx.draw_networkx_edges(G_viz, pos, edgelist=positive_edges, edge_color='#00ff88',
                               alpha=0.3, width=0.5, ax=ax, arrows=False)
    if negative_edges:
        nx.draw_networkx_edges(G_viz, pos, edgelist=negative_edges, edge_color='#ff4444',
                               alpha=0.5, width=0.8, ax=ax, arrows=False)

    # Draw nodes
    nx.draw_networkx_nodes(G_viz, pos, node_color=node_colors, node_size=node_sizes,
                           alpha=0.85, ax=ax, edgecolors='white', linewidths=0.5)

    ax.set_title('Bitcoin OTC Trust Network\nNode size = PageRank | Color = Community',
                 fontsize=18, fontweight='bold', color='white', pad=20)
    ax.axis('off')

    # Add legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#00ff88',
                   markersize=10, label='Trust Edge (green)', linestyle='None'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#ff4444',
                   markersize=10, label='Distrust Edge (red)', linestyle='None'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='gray',
                   markersize=15, label='High PageRank', alpha=0.8, linestyle='None'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='gray',
                   markersize=6, label='Low PageRank', alpha=0.8, linestyle='None')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10,
              facecolor='#2a2a4e', edgecolor='white', labelcolor='white')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
    plt.close()

    return output_path


def create_pyvis_interactive(G_trust, nodes_to_include, pagerank_scores, partition,
                             width='100%', height='700px'):
    """
    Create interactive PyVis network visualization.
    Limited to manageable number of nodes for readability.
    """
    # Limit nodes for readability
    max_nodes = min(80, len(nodes_to_include))
    nodes_to_show = nodes_to_include[:max_nodes]

    # Create PyVis network with dark theme
    net = Network(width=width, height=height, bgcolor='#1a1a2e', font_color='#ffffff')
    net.barnes_hut(gravity=-3000, central_gravity=0.3, spring_length=150, spring_strength=0.01)

    # Create subgraph
    subgraph = G_trust.subgraph(nodes_to_show)

    # Calculate size scaling
    pr_values = [pagerank_scores.get(n, 0) for n in nodes_to_show]
    max_pr = max(pr_values) if pr_values else 1
    min_pr = min(pr_values) if pr_values else 0
    pr_range = max_pr - min_pr + 0.0001

    # Add nodes
    for node in subgraph.nodes():
        pr_score = pagerank_scores.get(node, 0)
        comm = partition.get(node, 0)

        # Scale size between 15 and 50
        normalized_pr = (pr_score - min_pr) / pr_range
        size = 15 + normalized_pr * 35

        color = COMMUNITY_COLORS[comm % len(COMMUNITY_COLORS)]

        # Get rank among displayed nodes
        rank = sorted(pr_values, reverse=True).index(pr_score) + 1 if pr_score in pr_values else 0

        net.add_node(
            int(node),
            label=f"#{rank}" if rank <= 20 else str(node),
            size=size,
            color=color,
            title=f"<b>User {node}</b><br>Rank: #{rank}<br>PageRank: {pr_score:.6f}<br>Community: {comm}",
            font={'size': 12, 'color': 'white'}
        )

    # Add edges with rating-based coloring
    for u, v, data in subgraph.edges(data=True):
        rating = data.get('rating', 1)
        edge_color = '#44ff88' if rating > 0 else '#ff4444'
        width = 1 + abs(rating) / 5

        net.add_edge(int(u), int(v), color=edge_color, width=width,
                     title=f"Rating: {rating:+d}")

    # Generate HTML
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as f:
        net.save_graph(f.name)
        with open(f.name, 'r') as f2:
            html = f2.read()
        os.unlink(f.name)

    return html


def plot_rating_distribution(df):
    """Create Plotly histogram of rating distribution with better styling."""
    rating_counts = df['rating'].value_counts().sort_index().reset_index()
    rating_counts.columns = ['Rating', 'Count']

    # Color based on rating sign
    rating_counts['Color'] = rating_counts['Rating'].apply(
        lambda x: '#ff4444' if x < 0 else '#00ff88' if x > 0 else '#ffd93d'
    )

    fig = go.Figure()

    # Add bars with custom colors
    for _, row in rating_counts.iterrows():
        fig.add_trace(go.Bar(
            x=[row['Rating']],
            y=[row['Count']],
            marker_color=row['Color'],
            showlegend=False,
            hovertemplate=f"Rating: {row['Rating']}<br>Count: {row['Count']:,}<extra></extra>"
        ))

    fig.update_layout(
        title={
            'text': 'Rating Distribution: The J-Curve of Trust',
            'font': {'size': 20, 'color': '#ffffff'}
        },
        xaxis_title='Rating Score',
        yaxis_title='Frequency (log scale)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e0e0e0', size=14),
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            tickmode='linear',
            tick0=-10,
            dtick=1
        ),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)', type='log'),
        height=450,
        bargap=0.1
    )

    # Add annotation explaining the J-curve
    fig.add_annotation(
        x=8, y=0.85, xref='x', yref='paper',
        text="J-Curve: Most ratings<br>cluster at +10 (high trust)",
        showarrow=True, arrowhead=2, ax=-50, ay=-40,
        font=dict(color='#00ff88', size=12),
        arrowcolor='#00ff88'
    )

    return fig


def plot_centrality_comparison(pagerank_df):
    """Create comparison chart for centrality metrics."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=pagerank_df['Node'].astype(str),
        y=pagerank_df['PageRank'],
        name='PageRank',
        marker_color='#00ff88',
        text=[f"#{i+1}" for i in range(len(pagerank_df))],
        textposition='outside',
        textfont=dict(color='white', size=10)
    ))

    fig.update_layout(
        title='Top Nodes by PageRank Score',
        xaxis_title='User ID',
        yaxis_title='PageRank Score',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff'),
        height=400
    )

    return fig


def plot_degree_distribution(G):
    """Plot degree distribution with power law indication."""
    degrees = [d for n, d in G.degree()]

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=degrees,
        nbinsx=50,
        marker_color='#00ccff',
        opacity=0.8
    ))

    fig.update_layout(
        title='Degree Distribution (Power Law Pattern)',
        xaxis_title='Degree (number of connections)',
        yaxis_title='Count',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff'),
        height=350,
        yaxis_type='log'
    )

    return fig


def create_centrality_subgraph_viz(G_trust, pagerank_scores, top_n=20):
    """
    Create interactive visualization of top N nodes by centrality.
    Focused, readable graph showing trust anchors and their connections.
    """
    # Get top N nodes
    top_nodes = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    top_node_ids = [n for n, _ in top_nodes]
    top_scores = {n: s for n, s in top_nodes}

    # Create subgraph of just these nodes
    subgraph = G_trust.subgraph(top_node_ids)

    # Create PyVis network
    net = Network(width='100%', height='600px', bgcolor='#1a1a2e', font_color='#ffffff')
    net.barnes_hut(gravity=-2000, central_gravity=0.5, spring_length=200, spring_strength=0.01)

    # Color gradient from green (top) to blue (lower ranked)
    for rank, (node, score) in enumerate(top_nodes, 1):
        # Gradient: #00ff88 (green) -> #00ccff (cyan) -> #4d96ff (blue)
        if rank <= 7:
            color = '#00ff88'  # Top tier - bright green
        elif rank <= 14:
            color = '#00ccff'  # Mid tier - cyan
        else:
            color = '#4d96ff'  # Lower tier - blue

        # Size based on rank (larger = higher rank)
        size = 45 - (rank * 1.5)  # 45 down to ~15

        net.add_node(
            int(node),
            label=f"#{rank}\nUser {node}",
            size=max(size, 15),
            color=color,
            title=f"<b>Rank #{rank}</b><br>User ID: {node}<br>PageRank: {score:.6f}<br>In-degree: {G_trust.in_degree(node)}",
            font={'size': 14, 'color': 'white', 'face': 'arial'},
            borderWidth=2,
            borderWidthSelected=4
        )

    # Add edges between top nodes
    for u, v, data in subgraph.edges(data=True):
        rating = data.get('rating', 5)
        net.add_edge(
            int(u), int(v),
            color='rgba(0, 255, 136, 0.6)',
            width=1 + rating / 3,
            title=f"Trust rating: +{rating}"
        )

    # Generate HTML
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as f:
        net.save_graph(f.name)
        with open(f.name, 'r') as f2:
            html = f2.read()
        os.unlink(f.name)

    return html


def create_community_viz(G_trust, partition, community_sizes, num_communities=3, max_nodes_per_community=30):
    """
    Visualize communities with proper sampling for readability.
    Shows representative nodes from each community with inter-community edges.
    """
    # Get largest communities
    largest_comms = sorted(community_sizes.items(), key=lambda x: x[1], reverse=True)[:num_communities]
    comm_ids = [c for c, _ in largest_comms]

    # Sample nodes from each community for readability
    nodes_to_show = []
    node_community_map = {}

    for comm_id in comm_ids:
        comm_nodes = [n for n, c in partition.items() if c == comm_id]

        # Sample if community is too large
        if len(comm_nodes) > max_nodes_per_community:
            # Prefer nodes with higher degree
            if G_trust.is_directed():
                G_und = G_trust.to_undirected()
            else:
                G_und = G_trust
            node_degrees = [(n, G_und.degree(n)) for n in comm_nodes if n in G_und]
            node_degrees.sort(key=lambda x: x[1], reverse=True)
            sampled = [n for n, _ in node_degrees[:max_nodes_per_community]]
        else:
            sampled = comm_nodes

        for n in sampled:
            nodes_to_show.append(n)
            node_community_map[n] = comm_id

    # Create subgraph
    subgraph = G_trust.subgraph(nodes_to_show)

    # Create PyVis
    net = Network(width='100%', height='600px', bgcolor='#1a1a2e', font_color='#ffffff')
    net.barnes_hut(gravity=-1500, central_gravity=0.2, spring_length=120)

    # Add nodes with community colors
    for node in subgraph.nodes():
        comm = node_community_map.get(node, 0)
        comm_index = comm_ids.index(comm) if comm in comm_ids else 0
        color = COMMUNITY_COLORS[comm_index % len(COMMUNITY_COLORS)]
        comm_size = community_sizes.get(comm, 0)

        net.add_node(
            int(node),
            label=str(node),
            size=18,
            color=color,
            title=f"<b>User {node}</b><br>Community: {comm}<br>Community Size: {comm_size:,}",
            font={'size': 10, 'color': 'white'}
        )

    # Add edges - highlight inter-community edges
    for u, v in subgraph.edges():
        u_comm = node_community_map.get(u, -1)
        v_comm = node_community_map.get(v, -1)

        if u_comm != v_comm:
            # Inter-community edge - make it visible
            net.add_edge(int(u), int(v), color='#ff6b6b', width=2,
                        title="Inter-community connection")
        else:
            # Intra-community edge
            net.add_edge(int(u), int(v), color='rgba(255,255,255,0.2)', width=0.5)

    # Generate HTML
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as f:
        net.save_graph(f.name)
        with open(f.name, 'r') as f2:
            html = f2.read()
        os.unlink(f.name)

    return html


def create_suspicious_community_viz(G_trust, suspicious_communities, partition, max_display=5):
    """
    Visualize suspicious (potentially fraudulent) communities.
    These are small, isolated clusters that may be Sybil attack rings.
    """
    if not suspicious_communities:
        return "<div style='color: #00ff88; padding: 20px;'><h3>No suspicious communities detected</h3></div>"

    # Create PyVis
    net = Network(width='100%', height='600px', bgcolor='#1a1a2e', font_color='#ffffff')
    net.barnes_hut(gravity=-500, central_gravity=0.8, spring_length=80)

    # Show up to max_display suspicious communities
    for i, comm_info in enumerate(suspicious_communities[:max_display]):
        comm_users = comm_info.get('Users', [])
        comm_id = comm_info.get('Community ID', i)

        color = '#ff4444' if i == 0 else COMMUNITY_COLORS[(i + 5) % len(COMMUNITY_COLORS)]

        for node in comm_users:
            net.add_node(
                int(node),
                label=str(node),
                size=20,
                color=color,
                title=f"<b>SUSPICIOUS</b><br>User {node}<br>Community {comm_id}<br>Size: {len(comm_users)}",
                font={'size': 12, 'color': 'white'},
                borderWidth=3
            )

        # Add edges within this community
        subgraph = G_trust.subgraph(comm_users)
        for u, v in subgraph.edges():
            net.add_edge(int(u), int(v), color=color, width=2)

    # Generate HTML
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as f:
        net.save_graph(f.name)
        with open(f.name, 'r') as f2:
            html = f2.read()
        os.unlink(f.name)

    return html


def create_path_viz(G_trust, path, pagerank_scores=None):
    """
    Visualize shortest path with clear highlighting.
    Shows path nodes prominently with minimal context.
    """
    if not path or len(path) < 2:
        return "<div style='color: #ffd93d; padding: 20px;'><h3>No path to visualize</h3></div>"

    # Get only immediate neighbors for context (1 hop from path)
    context_nodes = set(path)
    for node in path:
        if node in G_trust:
            neighbors = list(G_trust.successors(node)) + list(G_trust.predecessors(node))
            # Add only a few neighbors for context
            context_nodes.update(neighbors[:5])

    # Limit total nodes
    if len(context_nodes) > 50:
        context_nodes = set(path)

    # Create subgraph
    subgraph = G_trust.subgraph(context_nodes)

    # Create PyVis
    net = Network(width='100%', height='600px', bgcolor='#1a1a2e', font_color='#ffffff')
    net.barnes_hut(gravity=-1500, central_gravity=0.3, spring_length=150)

    # Path edges set
    path_edges = set((path[i], path[i + 1]) for i in range(len(path) - 1))

    # Add nodes
    for i, node in enumerate(path):
        if i == 0:
            color = '#00ff88'  # Start - green
            label = f"START\n{node}"
            size = 35
        elif i == len(path) - 1:
            color = '#ff6b6b'  # End - red
            label = f"END\n{node}"
            size = 35
        else:
            color = '#ffd93d'  # Path - yellow
            label = f"Step {i}\n{node}"
            size = 28

        net.add_node(
            int(node),
            label=label,
            size=size,
            color=color,
            title=f"<b>{'Source' if i == 0 else 'Target' if i == len(path) - 1 else f'Step {i}'}</b><br>User {node}",
            font={'size': 12, 'color': 'white'},
            borderWidth=3
        )

    # Add context nodes (not in path)
    for node in context_nodes - set(path):
        net.add_node(
            int(node),
            label=str(node),
            size=10,
            color='#666666',
            title=f"Context node: User {node}",
            font={'size': 8, 'color': '#888888'}
        )

    # Add edges
    for u, v, data in subgraph.edges(data=True):
        rating = data.get('rating', 0)
        if (u, v) in path_edges:
            # Path edge - highlight strongly
            net.add_edge(int(u), int(v), color='#ffd93d', width=5,
                        title=f"PATH EDGE<br>Rating: +{rating}")
        else:
            # Context edge
            net.add_edge(int(u), int(v), color='rgba(255,255,255,0.15)', width=0.5)

    # Generate HTML
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as f:
        net.save_graph(f.name)
        with open(f.name, 'r') as f2:
            html = f2.read()
        os.unlink(f.name)

    return html


def create_component_viz(G, show_largest=True, show_smallest_n=0, max_nodes=100):
    """
    Visualize components with reasonable node limits.
    """
    # Get components
    if G.is_directed():
        components = list(nx.weakly_connected_components(G))
    else:
        components = list(nx.connected_components(G))

    # Sort by size
    components.sort(key=len, reverse=True)

    if not components:
        return "<div style='color: #ffd93d; padding: 20px;'><h3>No components found</h3></div>"

    # Select which to show
    if show_largest:
        # Show sample from largest component
        selected_nodes = list(components[0])
        if len(selected_nodes) > max_nodes:
            # Sample nodes with higher degree
            G_comp = G.subgraph(selected_nodes)
            degrees = dict(G_comp.degree())
            selected_nodes = sorted(degrees.keys(), key=lambda x: degrees[x], reverse=True)[:max_nodes]
        title_text = f"Largest Component (showing {len(selected_nodes)} of {len(components[0])} nodes)"
        single_component = True
    elif show_smallest_n > 0:
        # Show smallest components entirely
        selected_nodes = []
        component_assignments = {}
        for i, comp in enumerate(components[-show_smallest_n:]):
            for node in comp:
                selected_nodes.append(node)
                component_assignments[node] = i
        title_text = f"Smallest {show_smallest_n} Components ({len(selected_nodes)} nodes total)"
        single_component = False
    else:
        selected_nodes = list(components[0])[:max_nodes]
        title_text = "Component View"
        single_component = True

    # Create subgraph
    subgraph = G.subgraph(selected_nodes)

    # Create PyVis
    net = Network(width='100%', height='600px', bgcolor='#1a1a2e', font_color='#ffffff')
    net.barnes_hut(gravity=-2000, central_gravity=0.3, spring_length=100)

    # Add nodes
    for node in subgraph.nodes():
        if single_component:
            color = '#00ff88'
        else:
            comp_idx = component_assignments.get(node, 0)
            color = COMMUNITY_COLORS[comp_idx % len(COMMUNITY_COLORS)]

        net.add_node(
            int(node),
            label=str(node),
            size=15,
            color=color,
            title=f"User {node}<br>Degree: {subgraph.degree(node)}",
            font={'size': 9, 'color': 'white'}
        )

    # Add edges
    for u, v, data in subgraph.edges(data=True):
        rating = data.get('rating', 0)
        edge_color = 'rgba(0,255,136,0.4)' if rating > 0 else 'rgba(255,68,68,0.4)'
        net.add_edge(int(u), int(v), color=edge_color, width=0.8)

    # Generate HTML
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as f:
        net.save_graph(f.name)
        with open(f.name, 'r') as f2:
            html = f2.read()
        os.unlink(f.name)

    return html


def create_reachability_viz(G_trust, source_node, reachability_data, max_nodes_per_hop=15):
    """
    Visualize trust radius/reachability from a source node.
    Shows concentric circles of nodes at different hop distances.
    """
    net = Network(width='100%', height='600px', bgcolor='#1a1a2e', font_color='#ffffff')
    net.barnes_hut(gravity=-1500, central_gravity=0.5, spring_length=100)

    # Colors for different hop distances
    hop_colors = {
        0: '#ff6b6b',   # Source - red
        1: '#00ff88',   # 1-hop - green
        2: '#00ccff',   # 2-hop - cyan
        3: '#c44dff',   # 3-hop - purple
    }

    nodes_added = set()

    # Add source node
    net.add_node(
        int(source_node),
        label=f"SOURCE\n{source_node}",
        size=40,
        color=hop_colors[0],
        title=f"<b>Source Node</b><br>User {source_node}",
        font={'size': 14, 'color': 'white'},
        borderWidth=3
    )
    nodes_added.add(source_node)

    # Add nodes at each hop distance
    reachable_at_hop = reachability_data.get('reachable_at_hop', {})

    for hop in range(1, 4):
        # This would need the actual nodes, not just counts
        # For now, we'll use BFS to get actual nodes
        from collections import deque
        if hop == 1:
            hop_nodes = list(G_trust.successors(source_node)) if source_node in G_trust else []
        else:
            # Get nodes at this hop distance
            hop_nodes = []
            queue = deque([(source_node, 0)])
            visited = {source_node}
            while queue:
                node, dist = queue.popleft()
                if dist == hop:
                    hop_nodes.append(node)
                elif dist < hop and node in G_trust:
                    for neighbor in G_trust.successors(node):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append((neighbor, dist + 1))

        # Sample if too many
        if len(hop_nodes) > max_nodes_per_hop:
            hop_nodes = random.sample(hop_nodes, max_nodes_per_hop)

        for node in hop_nodes:
            if node not in nodes_added:
                net.add_node(
                    int(node),
                    label=str(node),
                    size=25 - (hop * 5),
                    color=hop_colors.get(hop, '#666666'),
                    title=f"<b>{hop}-hop from source</b><br>User {node}",
                    font={'size': 10, 'color': 'white'}
                )
                nodes_added.add(node)

    # Add edges between shown nodes
    subgraph = G_trust.subgraph(nodes_added)
    for u, v in subgraph.edges():
        net.add_edge(int(u), int(v), color='rgba(255,255,255,0.3)', width=1)

    # Generate HTML
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as f:
        net.save_graph(f.name)
        with open(f.name, 'r') as f2:
            html = f2.read()
        os.unlink(f.name)

    return html
