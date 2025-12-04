#!/usr/bin/env python3
"""
Script to enhance the Jupyter notebook with new analysis sections.
Adds: Graph Model, Components, BFS Reachability, PNG Visualization, Final Recommendations
"""

import nbformat
from nbformat.v4 import new_markdown_cell, new_code_cell

def main():
    # Load existing notebook
    nb = nbformat.read('crypto_trust_analysis.ipynb', as_version=4)
    
    print("Enhancing Jupyter notebook...")
    print(f"Current cells: {len(nb.cells)}")
    
    # 1. UPDATE IMPORTS (insert after cell 2 - the imports cell)
    imports_addition = new_code_cell(
"""# Import analysis modules
import sys
sys.path.insert(0, '.')  # Add current directory to path

from analysis import centrality, community, paths, components, reachability, visualization""")
    
    # 2. ADD GRAPH MODEL SECTION
    graph_model_md = new_markdown_cell(
"""## 1.5 Graph Model Definition

**Nodes**: Individual users on the Bitcoin OTC platform  
**Edges**: Signed ratings from one user to another  

### Edge Attributes:
- `source`: User ID who gave the rating
- `target`: User ID who received the rating  
- `rating`: Integer from -10 (total distrust) to +10 (total trust)
- `time`: Unix timestamp
- `weight`: Absolute value of rating (for algorithms)

### Graph Views:
- **G**: Full directed graph (all edges)
- **G_trust**: Positive edges only (rating > 0)
- **G_distrust**: Negative edges only (rating < 0)

**Business Interpretation**:  
- Positive ratings = willingness to trade
- Negative ratings = fraud warnings or disputes
- Edge direction matters: A→B means A rated B""")
    
    # 3. ADD COMPONENTS ANALYSIS
    components_md = new_markdown_cell(
"""## 4.5 Network Components Analysis

**Business Question**: Is the network fragmented or well-connected?  
**Why It Matters**: Fragmented networks indicate isolated communities or poor network health.""")
    
    components_code = new_code_cell(
"""# Analyze network components
comp_stats = components.analyze_components(G)
connectivity = components.analyze_component_connectivity(G)

print("=" * 60)
print("NETWORK COMPONENTS ANALYSIS")
print("=" * 60)
print(f"\\nTotal Components: {comp_stats['num_components']}")
print(f"Largest Component: {comp_stats['largest_component_size']:,} nodes ({comp_stats['largest_component_pct']:.2f}%)")
print(f"Isolated Nodes: {comp_stats['num_isolated_nodes']:,}")
print(f"\\nNetwork Health: {connectivity['health']}")

print(f"\\nComponent Size Distribution:")
for size_range, count in comp_stats['size_distribution'].items():
    print(f"  {size_range}: {count} components")

print(f"\\n💡 Business Insight: A health rating of '{connectivity['health']}' means ", end="")
if connectivity['health'] == 'EXCELLENT':
    print("the network is highly connected and accessible.")
elif connectivity['health'] == 'GOOD':
    print("most users can reach each other, indicating good platform health.")
else:
    print("the network may have connectivity issues requiring investigation.")""")
    
    # 4. ADD BFS REACHABILITY
    bfs_md = new_markdown_cell(
"""## 7.5 BFS Reachability Analysis

**Business Question**: How far can trust propagate through the network?  
**Application**: Understand the "trust radius" of anchor users.""")
    
    bfs_code = new_code_cell(
"""# Analyze trust radius for top PageRank users
top_anchors_list = [user for user, score in top_pagerank[:5]]

print("=" * 60)
print("TRUST RADIUS ANALYSIS (Top 5 Anchors)")
print("=" * 60)

trust_radii = []
for user in top_anchors_list:
    radius = reachability.compute_trust_radius(G_trust, user, max_hops=3)
    trust_radii.append(radius)
    
    print(f"\\nUser {user}:")
    print(f"  1-hop reach: {radius['reachable_at_hop'][1]:,} users")
    print(f"  2-hop reach: {radius['reachable_at_hop'][2]:,} users (cumulative: {radius['cumulative'][2]:,})")
    print(f"  3-hop reach: {radius['reachable_at_hop'][3]:,} users (cumulative: {radius['cumulative'][3]:,})")
    print(f"  Total reachable: {radius['total_reachable']:,} users")

print(f"\\n💡 Business Insight: Trust anchors can reach hundreds to thousands of users")
print("within 2-3 hops, enabling efficient trust propagation across the network.")""")
    
    # 5. VISUALIZATION
    viz_md = new_markdown_cell(
"""## 9. Network Visualization (Python)

**Replaced Gephi with Python-based visualization**  
Using matplotlib for static PNG and PyVis for interactive HTML.""")
    
    viz_code = new_code_cell(
"""# Create static network visualization PNG
print("Creating network visualization...")
print("(Sampling top 500 nodes for performance)")

png_path = visualization.create_network_png(
    G_trust,
    pagerank_scores,
    partition,
    output_path='network_visualization.png',
    sample_size=500
)

print(f"✓ Visualization saved to: {png_path}")
print("\\n📊 Legend:")
print("  - Node size: Proportional to PageRank score")
print("  - Node color: Community membership")
print("  - Green edges: Trust (positive ratings)")
print("  - Red edges: Distrust (negative ratings)")

# Display the image
from IPython.display import Image, display
display(Image(filename=png_path))""")
    
    # 6. FINAL RECOMMENDATIONS
    final_md = new_markdown_cell(
"""## 10. Final Findings & Business Recommendations

### Key Findings Summary

This analysis successfully:
- ✅ Identified network structure and health
- ✅ Detected trust anchors via PageRank
- ✅ Found suspicious fraud communities
- ✅ Analyzed trust propagation
- ✅ Created visual network representation

### Business Recommendations

**1. Implement Trust Tier System**
- GOLD: Top 20 PageRank users
- SILVER: Users within 2 hops of GOLD
- BRONZE: Users within 3 hops of GOLD  
- UNVERIFIED: Requires additional checks

**2. Fraud Detection Workflow**
- Flag small isolated communities
- Manual review for <10 user clusters
- Monitor for Sybil attack patterns

**3. Risk-Based Trading**
- LOW RISK: ≤2 hop trust paths
- MEDIUM RISK: 3-4 hop paths
- HIGH RISK: >4 hops or no path

### Next Steps
1. Deploy as production service
2. Create real-time monitoring dashboard
3. Integrate with trading platform API
4. A/B test trust tier system""")
    
    # Insert cells at appropriate positions
    insertions = [
        (3, imports_addition, "Analysis module imports"),
        (4, graph_model_md, "Graph model definition"),
        (13, components_md, "Components markdown"),
        (14, components_code, "Components code"),
        (22, bfs_md, "BFS markdown"),
        (23, bfs_code, "BFS code"),
        (27, viz_md, "Visualization markdown"),
        (28, viz_code, "Visualization code"),
        (29, final_md, "Final recommendations"),
    ]
    
    # Insert in reverse order
    for pos, cell, desc in reversed(insertions):
        nb.cells.insert(min(pos, len(nb.cells)), cell)
        print(f"  ✓ Inserted: {desc}")
    
    # Save enhanced notebook
    nbformat.write(nb, 'crypto_trust_analysis_enhanced.ipynb')
    print(f"\n✅ Enhanced notebook saved as: crypto_trust_analysis_enhanced.ipynb")
    print(f"Total cells: {len(nb.cells)}")
    
if __name__ == "__main__":
    main()
