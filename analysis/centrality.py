"""
Centrality Analysis Module

Functions for computing and analyzing network centrality metrics.
"""

import networkx as nx
import pandas as pd


def compute_degree_centrality(G):
    """
    Compute degree centrality for all nodes.
    
    Args:
        G: NetworkX graph
        
    Returns:
        dict: {node: centrality_score}
    """
    return nx.degree_centrality(G)


def compute_pagerank(G_trust, weight='weight'):
    """
    Compute PageRank on trust network.
    
    Args:
        G_trust: Trust subgraph (positive edges only)
        weight: Edge attribute to use as weight
        
    Returns:
        dict: {node: pagerank_score}
    """
    if G_trust.number_of_nodes() == 0:
        return {}
    return nx.pagerank(G_trust, weight=weight)


def compute_betweenness_centrality(G, k=None):
    """
    Compute betweenness centrality.
    
    Args:
        G: NetworkX graph
        k: Number of nodes to sample (None for all)
        
    Returns:
        dict: {node: betweenness_score}
    """
    if G.number_of_nodes() == 0:
        return {}
    return nx.betweenness_centrality(G, k=k)


def get_top_nodes(centrality_dict, n=20):
    """
    Get top N nodes by centrality score.
    
    Args:
        centrality_dict: Dictionary of {node: score}
        n: Number of top nodes to return
        
    Returns:
        list: [(node, score), ...] sorted descending
    """
    return sorted(centrality_dict.items(), key=lambda x: x[1], reverse=True)[:n]


def compare_centralities(pagerank_scores, degree_scores, betweenness_scores=None, top_n=20):
    """
    Create comparison DataFrame of different centrality measures.
    
    Args:
        pagerank_scores: PageRank dict
        degree_scores: Degree centrality dict
        betweenness_scores: Betweenness centrality dict (optional)
        top_n: Number of top nodes to include
        
    Returns:
        pd.DataFrame: Comparison table
    """
    # Get top nodes by PageRank
    top_pr = get_top_nodes(pagerank_scores, top_n)
    
    data = []
    for rank, (node, pr_score) in enumerate(top_pr, 1):
        row = {
            'Rank': rank,
            'Node': node,
            'PageRank': pr_score,
            'Degree': degree_scores.get(node, 0)
        }
        if betweenness_scores:
            row['Betweenness'] = betweenness_scores.get(node, 0)
        data.append(row)
    
    return pd.DataFrame(data)


def analyze_centrality_distribution(centrality_dict):
    """
    Analyze distribution of centrality scores.
    
    Args:
        centrality_dict: Dictionary of {node: score}
        
    Returns:
        dict: Statistics about distribution
    """
    scores = list(centrality_dict.values())
    
    if not scores:
        return {}
    
    import numpy as np
    
    return {
        'mean': np.mean(scores),
        'median': np.median(scores),
        'std': np.std(scores),
        'min': np.min(scores),
        'max': np.max(scores),
        'total_nodes': len(scores)
    }
