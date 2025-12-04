"""
Community Detection Module

Functions for detecting and analyzing communities in trust networks.
"""

import networkx as nx
from collections import Counter
try:
    import community.community_louvain as community_louvain
except ImportError:
    import community as community_louvain


def detect_communities(G_trust):
    """
    Detect communities using Louvain algorithm.
    
    Args:
        G_trust: Trust subgraph (undirected or will be converted)
        
    Returns:
        tuple: (partition dict, community_sizes Counter)
    """
    if G_trust.number_of_nodes() == 0:
        return {}, Counter()
    
    # Convert to undirected for Louvain
    if G_trust.is_directed():
        G_undirected = G_trust.to_undirected()
    else:
        G_undirected = G_trust
    
    partition = community_louvain.best_partition(G_undirected, weight='weight')
    community_sizes = Counter(partition.values())
    
    return partition, community_sizes


def find_suspicious_communities(G_trust, partition, community_sizes, max_size=10):
    """
    Identify small, isolated communities as potential fraud rings.
    
    Args:
        G_trust: Trust graph
        partition: Community partition dict
        community_sizes: Counter of community sizes
        max_size: Maximum size for suspicious communities
        
    Returns:
        list: List of suspicious community dicts
    """
    if G_trust.number_of_nodes() == 0:
        return []
    
    # Get undirected version
    if G_trust.is_directed():
        G_undirected = G_trust.to_undirected()
    else:
        G_undirected = G_trust
    
    # Find largest connected component
    largest_cc = max(nx.connected_components(G_undirected), key=len)
    
    suspicious = []
    for comm_id, size in community_sizes.items():
        if size < max_size:
            # Get users in this community
            comm_users = [user for user, c in partition.items() if c == comm_id]
            
            # Check if isolated from main component
            connections_to_main = 0
            for user in comm_users:
                if user in G_undirected:
                    neighbors = set(G_undirected.neighbors(user))
                    if neighbors & largest_cc:
                        connections_to_main += 1
                        break
            
            if connections_to_main == 0:
                suspicious.append({
                    'Community ID': comm_id,
                    'Size': size,
                    'Users': comm_users[:10]  # Show first 10
                })
    
    return suspicious


def analyze_community_structure(partition, community_sizes):
    """
    Analyze community structure statistics.
    
    Args:
        partition: Community partition dict
        community_sizes: Counter of community sizes
        
    Returns:
        dict: Community statistics
    """
    if not community_sizes:
        return {
            'total_communities': 0,
            'largest_community_size': 0,
            'smallest_community_size': 0,
            'average_community_size': 0,
            'total_nodes': 0
        }
    
    sizes = list(community_sizes.values())
    
    return {
        'total_communities': len(community_sizes),
        'largest_community_size': max(sizes),
        'smallest_community_size': min(sizes),
        'average_community_size': sum(sizes) / len(sizes),
        'total_nodes': sum(sizes),
        'size_distribution': {
            '1 node': sum(1 for s in sizes if s == 1),
            '2-10 nodes': sum(1 for s in sizes if 2 <= s <= 10),
            '11-50 nodes': sum(1 for s in sizes if 11 <= s <= 50),
            '50+ nodes': sum(1 for s in sizes if s > 50)
        }
    }


def get_community_members(partition, community_id):
    """
    Get all members of a specific community.
    
    Args:
        partition: Community partition dict
        community_id: ID of community to retrieve
        
    Returns:
        list: Node IDs in the community
    """
    return [node for node, comm_id in partition.items() if comm_id == community_id]


def get_intercommunity_edges(G, partition):
    """
    Count edges between different communities.
    
    Args:
        G: NetworkX graph
        partition: Community partition dict
        
    Returns:
        int: Number of edges between communities
    """
    inter_edges = 0
    for u, v in G.edges():
        if partition.get(u) != partition.get(v):
            inter_edges += 1
    return inter_edges
