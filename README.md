# Crypto-Trust: Bitcoin OTC Network Analysis

## Overview
This project provides **two complementary tools** for analyzing Bitcoin OTC trust networks to identify trust anchors and detect potential fraud rings:

1. **Jupyter Notebook**: Deep-dive data science analysis
2. **Streamlit Web App**: Interactive GUI for exploration

## Business Objectives
- **Trust Anchor Identification**: Find reliable, high-reputation users using PageRank
- **Fraud Ring Detection**: Identify potential Sybil attack clusters using community detection
- **Risk Assessment**: Evaluate new users based on their connectivity to trusted users

---

## 📊 Option 1: Jupyter Notebook Analysis

### What It Is
A comprehensive, self-contained Jupyter Notebook with detailed algorithmic analysis and visualizations.

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Launch notebook
jupyter notebook crypto_trust_analysis.ipynb
```

### Features
- ✅ Complete data science workflow
- ✅ 3 graph algorithms (PageRank, Louvain, Shortest Path)
- ✅ Matplotlib visualizations
- ✅ Gephi export for advanced visualization
- ✅ Detailed business insights

**Best for**: Data scientists, analysts, researchers

---

## 🌐 Option 2: Streamlit Web Application

### What It Is
A production-grade interactive web application with modern dark mode UI for exploring the trust network.

### Quick Start
```bash
# Install Streamlit dependencies
pip install -r requirements_streamlit.txt

# Launch app
streamlit run app.py

# Or use the automated launcher
bash run_streamlit.sh
```

The app opens automatically at `http://localhost:8501`

### Features
- ✅ **Modern Dark Mode UI** with glassmorphism effects
- ✅ **4 Interactive Tabs**:
  - 📊 Network Overview Dashboard
  - 🏆 Trust Algorithms Leaderboard
  - 🔀 Path Finder (find trust paths between users)
  - 🌐 Graph Explorer (interactive PyVis visualizations)
- ✅ **Performance Cached**: Lightning-fast subsequent loads
- ✅ **Interactive Charts**: Plotly with zoom/pan/hover
- ✅ **Dynamic Graphs**: Physics-based network visualization
- ✅ **No Coding Required**: Point-and-click interface

**Best for**: Business users, stakeholders, live demos

---

## 🎯 Which Tool Should I Use?

| Use Case | Tool | Why |
|----------|------|-----|
| Data exploration & analysis | Jupyter Notebook | Full control, export to Gephi |
| Live demo / presentation | Streamlit App | No code, interactive, visual |
| Business stakeholder review | Streamlit App | User-friendly, no setup |
| Research & experimentation | Jupyter Notebook | Modify algorithms, add new ones |
| Production deployment | Streamlit App | Cloud-ready, scalable |

---

## 🚀 Quick Demo

### Streamlit (Recommended - 1-minute demo)
```bash
bash run_streamlit.sh
```

1. Click "Run Analysis" in sidebar
2. Explore the 4 tabs
3. Try the Path Finder
4. Visualize communities

### Jupyter (5-minute demo)
```bash
jupyter notebook crypto_trust_analysis.ipynb
```

---

## 📁 Key Files

- `app.py` - Streamlit web application
- `crypto_trust_analysis.ipynb` - Jupyter Notebook
- `requirements_streamlit.txt` - Streamlit dependencies
- `requirements.txt` - Jupyter dependencies
- `soc-sign-bitcoinotc.csv` - Dataset (35,592 edges)

---

## 🎓 Technical Stack

**Core**: Python 3.8+, NetworkX 3.0, python-louvain  
**Jupyter**: Matplotlib, seaborn  
**Streamlit**: Plotly 5.17+, PyVis 0.3.2+, Streamlit 1.28+

---

## 📄 License
MIT
