"""
Reachability Analysis Module

Functions for BFS-based reachability and trust radius analysis.
"""

import networkx as nx
import pandas as pd


def bfs_reachability(G, source, max_depth=3):
    """
    Compute BFS reachability from a source node.
    
    Args:
        G: NetworkX graph
        source: Source node
        max_depth: Maximum depth to explore
        
    Returns:
        dict: {depth: [nodes at that depth]}
    """
    if source not in G:
        return {}
    
    # BFS tree from source
    bfs_tree = nx.bfs_tree(G, source, depth_limit=max_depth)
    
    # Organize nodes by depth
    depths = {}
    for depth in range(max_depth + 1):
        depths[depth] = []
    
    # Get distances from source
    distances = nx.single_source_shortest_path_length(G, source, cutoff=max_depth)
    
    for node, dist in distances.items():
        if node != source:  # Exclude source itself
            depths[dist].append(node)
    
    return depths


def compute_trust_radius(G_trust, user, max_hops=3):
    """
    Compute trust radius - how many users are reachable at different hop distances.
    
    Args:
        G_trust: Trust graph
        user: User node
        max_hops: Maximum hops to check
        
    Returns:
        dict: {
            'user': user,
            'reachable_at_hop': {1: count, 2: count, 3: count},
            'cumulative': {1: count, 2: count, 3: count},
            'total_reachable': int
        }
    """
    depths = bfs_reachability(G_trust, user, max_depth=max_hops)
    
    reachable_at_hop = {}
    cumulative = {}
    total = 0
    
    for hop in range(1, max_hops + 1):
        reachable_at_hop[hop] = len(depths.get(hop, []))
        total += reachable_at_hop[hop]
        cumulative[hop] = total
    
    return {
        'user': user,
        'reachable_at_hop': reachable_at_hop,
        'cumulative': cumulative,
        'total_reachable': total
    }


def analyze_network_reach(G_trust, sample_users=None, max_hops=3):
    """
    Analyze network reach for multiple users.
    
    Args:
        G_trust: Trust graph
        sample_users: List of users to analyze (None for all)
        max_hops: Maximum hops to check
        
    Returns:
        pd.DataFrame: Reachability analysis
    """
    if sample_users is None:
        # Sample top nodes by degree
        degrees = dict(G_trust.degree())
        sample_users = sorted(degrees, key=degrees.get, reverse=True)[:20]
    
    results = []
    for user in sample_users:
        if user in G_trust:
            radius = compute_trust_radius(G_trust, user, max_hops)
            
            row = {'User': user}
            for hop in range(1, max_hops + 1):
                row[f'{hop}_hop'] = radius['reachable_at_hop'][hop]
                row[f'{hop}_hop_cumulative'] = radius['cumulative'][hop]
            row['Total_Reachable'] = radius['total_reachable']
            
            results.append(row)
    
    return pd.DataFrame(results)


def compute_average_reachability(G, sample_size=100):
    """
    Compute average reachability across random nodes.
    
    Args:
        G: NetworkX graph
        sample_size: Number of nodes to sample
        
    Returns:
        dict: Average reachability metrics
    """
    import random
    import numpy as np
    
    nodes = list(G.nodes())
    sample = random.sample(nodes, min(sample_size, len(nodes)))
    
    reachabilities = []
    for node in sample:
        radius = compute_trust_radius(G, node, max_hops=3)
        reachabilities.append(radius['total_reachable'])
    
    return {
        'mean_reachability': np.mean(reachabilities),
        'median_reachability': np.median(reachabilities),
        'std_reachability': np.std(reachabilities),
        'max_reachability': np.max(reachabilities),
        'min_reachability': np.min(reachabilities)
    }


def get_unreachable_nodes(G, source, max_depth=3):
    """
    Find nodes that are not reachable from source within max_depth.
    
    Args:
        G: NetworkX graph
        source: Source node
        max_depth: Maximum depth to search
        
    Returns:
        set: Unreachable nodes
    """
    if source not in G:
        return set(G.nodes())
    
    # Get all reachable nodes
    reachable = set(nx.single_source_shortest_path_length(G, source, cutoff=max_depth).keys())
    
    # All nodes minus reachable
    all_nodes = set(G.nodes())
    unreachable = all_nodes - reachable
    
    return unreachable


def analyze_trust_propagation(G_trust, top_anchors, max_hops=3):
    """
    Analyze how trust propagates from top anchor nodes.
    
    Args:
        G_trust: Trust graph
        top_anchors: List of high-trust nodes
        max_hops: Maximum hops to analyze
        
    Returns:
        dict: Trust propagation analysis
    """
    covered_nodes = set()
    hop_coverage = {hop: set() for hop in range(1, max_hops + 1)}
    
    for anchor in top_anchors:
        if anchor in G_trust:
            depths = bfs_reachability(G_trust, anchor, max_depth=max_hops)
            
            for hop, nodes in depths.items():
                if hop > 0:
                    hop_coverage[hop].update(nodes)
                    covered_nodes.update(nodes)
    
    total_nodes = G_trust.number_of_nodes()
    
    return {
        'anchors_analyzed': len(top_anchors),
        'total_coverage': len(covered_nodes),
        'coverage_pct': (len(covered_nodes) / total_nodes * 100) if total_nodes > 0 else 0,
        'hop_coverage': {hop: len(nodes) for hop, nodes in hop_coverage.items()},
        'uncovered': total_nodes - len(covered_nodes)
    }
