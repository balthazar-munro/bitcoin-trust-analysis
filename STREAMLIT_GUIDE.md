# Streamlit Application Quick Start

## 🚀 Launch the Application

```bash
cd "/Users/balthazarmunro/Desktop/Antigravity Projects/Graph Analytics Project"

# Install dependencies (first time only)
pip install -r requirements_streamlit.txt

# Run the app
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

## 📱 Using the Application

### Step 1: Run Analysis
- Click "🚀 Run Analysis" in the sidebar
- Wait for data to load (~5-10 seconds)

### Step 2: Explore the Tabs

**📊 Network Overview**
- View network statistics (nodes, edges, ratings)
- See the J-curve rating distribution
- Compare top raters vs top rated users

**🏆 Trust Algorithms**
- View Top 20 Trust Anchors (PageRank leaderboard)
- Check for suspicious fraud rings
- Compare PageRank vs In-Degree metrics

**🔀 Path Finder**
- Select any two users from dropdowns
- Find shortest trust path between them
- See risk assessment and trust scores

**🌐 Graph Explorer**
- **Ego Network**: Visualize network around a specific user
- **Community Network**: Explore detected communities
- Interactive graph with physics simulation

## 🎨 Features

- **Modern Dark Mode** with glassmorphism effects
- **Performance Cached** - fast subsequent loads
- **Interactive Charts** - Plotly with zoom/pan/hover
- **Dynamic Graphs** - PyVis with physics simulation
- **Error Handling** - Graceful degradation

## ⚙️ Configuration

**Rating Threshold Filter** (Sidebar)
- Adjust slider to filter low-value edges
- Click "Run Analysis" to apply filter

**File Upload** (Sidebar)
- Upload custom CSV datasets
- Format: `source,target,rating,time`

## 🔧 Troubleshooting

**App won't start?**
```bash
pip install --upgrade streamlit plotly pyvis
```

**Graph not rendering?**
- Try a smaller community or lower ego radius
- Maximum 500 nodes for browser performance

**Data not loading?**
- Ensure `soc-sign-bitcoinotc.csv` is in project directory
- Or upload file via sidebar uploader

## 📝 Notes

- First analysis takes ~10-15 seconds (builds graph + computes algorithms)
- Subsequent interactions are instant (cached)
- Large ego networks (radius 3) may be slow to render
- PyVis graphs are interactive: drag nodes, zoom, pan
