"""
Network Components Module

Functions for analyzing connected components and network structure.
"""

import networkx as nx


def analyze_components(G):
    """
    Analyze weakly connected components in directed graph.
    
    Args:
        G: NetworkX directed graph
        
    Returns:
        dict: Component statistics
    """
    if G.number_of_nodes() == 0:
        return {
            'num_components': 0,
            'largest_component_size': 0,
            'largest_component_pct': 0,
            'num_isolated_nodes': 0,
            'component_sizes': []
        }
    
    # Get weakly connected components
    components = list(nx.weakly_connected_components(G))
    component_sizes = [len(c) for c in components]
    component_sizes.sort(reverse=True)
    
    largest_size = component_sizes[0] if component_sizes else 0
    num_nodes = G.number_of_nodes()
    
    # Count isolated nodes (components of size 1)
    isolated = sum(1 for size in component_sizes if size == 1)
    
    return {
        'num_components': len(components),
        'largest_component_size': largest_size,
        'largest_component_pct': (largest_size / num_nodes * 100) if num_nodes > 0 else 0,
        'num_isolated_nodes': isolated,
        'component_sizes': component_sizes,
        'size_distribution': {
            '1 node': sum(1 for s in component_sizes if s == 1),
            '2-10 nodes': sum(1 for s in component_sizes if 2 <= s <= 10),
            '11-100 nodes': sum(1 for s in component_sizes if 11 <= s <= 100),
            '100+ nodes': sum(1 for s in component_sizes if s > 100)
        }
    }


def compute_weakly_connected_components(G):
    """
    Get weakly connected components.
    
    Args:
        G: NetworkX directed graph
        
    Returns:
        list: List of sets, each containing nodes in a component
    """
    return list(nx.weakly_connected_components(G))


def compute_strongly_connected_components(G):
    """
    Get strongly connected components (for directed graphs).
    
    Args:
        G: NetworkX directed graph
        
    Returns:
        list: List of sets, each containing nodes in a component
    """
    return list(nx.strongly_connected_components(G))


def get_largest_component(G):
    """
    Get the largest weakly connected component.
    
    Args:
        G: NetworkX directed graph
        
    Returns:
        set: Nodes in largest component
    """
    if G.number_of_nodes() == 0:
        return set()
    
    components = nx.weakly_connected_components(G)
    return max(components, key=len)


def compute_network_coverage(G):
    """
    Compute what percentage of network is in largest component.
    
    Args:
        G: NetworkX graph
        
    Returns:
        float: Percentage (0-100)
    """
    if G.number_of_nodes() == 0:
        return 0.0
    
    largest = get_largest_component(G)
    return (len(largest) / G.number_of_nodes()) * 100


def analyze_component_connectivity(G):
    """
    Analyze connectivity strength of the network.
    
    Args:
        G: NetworkX directed graph
        
    Returns:
        dict: Connectivity metrics
    """
    stats = analyze_components(G)
    
    if stats['num_components'] == 0:
        return {'health': 'EMPTY'}
    
    coverage = stats['largest_component_pct']
    
    # Assess network health
    if coverage >= 90:
        health = 'EXCELLENT'
    elif coverage >= 75:
        health = 'GOOD'
    elif coverage >= 50:
        health = 'MODERATE'
    else:
        health = 'FRAGMENTED'
    
    return {
        'health': health,
        'coverage': coverage,
        'num_components': stats['num_components'],
        'fragmented': stats['num_components'] > 10,
        'has_isolated': stats['num_isolated_nodes'] > 0
    }


def find_bridge_nodes(G):
    """
    Find nodes that, if removed, would disconnect the graph.
    
    Args:
        G: NetworkX graph
        
    Returns:
        list: Bridge nodes
    """
    # Convert to undirected for bridge analysis
    if G.is_directed():
        G_und = G.to_undirected()
    else:
        G_und = G
    
    bridges = list(nx.articulation_points(G_und))
    return bridges
