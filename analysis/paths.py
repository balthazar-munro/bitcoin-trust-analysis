"""
Path Analysis Module

Functions for analyzing trust paths and risk assessment.
"""

import networkx as nx


def find_shortest_path(G, source, target):
    """
    Find shortest path between two nodes and compute metrics.
    
    Args:
        G: NetworkX graph
        source: Source node
        target: Target node
        
    Returns:
        dict: {
            'exists': bool,
            'path': list of nodes,
            'length': int hops,
            'total_trust': float,
            'average_trust': float,
            'error': str or None
        }
    """
    try:
        path = nx.shortest_path(G, source=source, target=target)
        path_length = len(path) - 1
        
        # Calculate trust score along path
        total_trust = sum(G[path[i]][path[i+1]]['rating'] for i in range(len(path)-1))
        avg_trust = total_trust / path_length if path_length > 0 else 0
        
        return {
            'exists': True,
            'path': path,
            'length': path_length,
            'total_trust': total_trust,
            'average_trust': avg_trust,
            'error': None
        }
    
    except nx.NetworkXNoPath:
        return {
            'exists': False,
            'path': [],
            'length': 0,
            'total_trust': 0,
            'average_trust': 0,
            'error': 'No path exists'
        }
    
    except nx.NodeNotFound as e:
        return {
            'exists': False,
            'path': [],
            'length': 0,
            'total_trust': 0,
            'average_trust': 0,
            'error': f'Node not found: {e}'
        }


def assess_path_risk(path_info):
    """
    Assess risk level based on path characteristics.
    
    Args:
        path_info: Dictionary from find_shortest_path()
        
    Returns:
        str: 'LOW', 'MEDIUM', 'ELEVATED', or 'HIGH'
    """
    if not path_info['exists']:
        return 'HIGH'
    
    length = path_info['length']
    avg_trust = path_info['average_trust']
    
    # Risk based on path length
    if length <= 2:
        length_risk = 'LOW'
    elif length <= 4:
        length_risk = 'MEDIUM'
    else:
        length_risk = 'ELEVATED'
    
    # Risk based on trust quality
    if avg_trust >= 8:
        trust_risk = 'LOW'
    elif avg_trust >= 5:
        trust_risk = 'MEDIUM'
    else:
        trust_risk = 'ELEVATED'
    
    # Combined risk (take worse of the two)
    risks = {'LOW': 0, 'MEDIUM': 1, 'ELEVATED': 2, 'HIGH': 3}
    combined_score = max(risks[length_risk], risks[trust_risk])
    
    for level, score in risks.items():
        if score == combined_score:
            return level
    
    return 'MEDIUM'


def analyze_path_quality(G, path):
    """
    Analyze quality metrics for a given path.
    
    Args:
        G: NetworkX graph
        path: List of nodes in path
        
    Returns:
        dict: Quality metrics
    """
    if len(path) < 2:
        return {'valid': False}
    
    ratings = []
    for i in range(len(path) - 1):
        rating = G[path[i]][path[i+1]].get('rating', 0)
        ratings.append(rating)
    
    return {
        'valid': True,
        'length': len(path) - 1,
        'min_rating': min(ratings),
        'max_rating': max(ratings),
        'avg_rating': sum(ratings) / len(ratings),
        'all_positive': all(r > 0 for r in ratings),
        'weakest_link': min(ratings)
    }


def compute_average_path_length(G, sample_size=100):
    """
    Compute average shortest path length on a sample of node pairs.
    
    Args:
        G: NetworkX graph
        sample_size: Number of random pairs to sample
        
    Returns:
        float: Average path length
    """
    import random
    
    if G.number_of_nodes() < 2:
        return 0
    
    nodes = list(G.nodes())
    paths_found = []
    
    for _ in range(sample_size):
        source = random.choice(nodes)
        target = random.choice(nodes)
        
        if source != target:
            try:
                length = nx.shortest_path_length(G, source, target)
                paths_found.append(length)
            except nx.NetworkXNoPath:
                continue
    
    if paths_found:
        return sum(paths_found) / len(paths_found)
    return 0
