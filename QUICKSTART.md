# 🚀 Quick Start Guide - Crypto-Trust Analysis

## ⚡ 1-Minute Setup

```bash
# Navigate to project
cd "/Users/balthazarmunro/Desktop/Antigravity Projects/Graph Analytics Project"

# Install dependencies (choose one method)

# Option A: Using pip directly
pip install -r requirements.txt

# Option B: Using setup script (creates virtual environment)
bash setup.sh
source venv/bin/activate
```

## ▶️ Run the Analysis

```bash
# Validate dataset (optional)
python3 validate_data.py

# Launch Jupyter Notebook
jupyter notebook crypto_trust_analysis.ipynb
```

Then simply **Run All Cells** in the notebook!

---

## 📊 What You'll Get

### 1. **Trust Anchors** (PageRank)
- Top 10 most trustworthy users
- Comparison: PageRank vs. In-Degree
- Network influence scores

### 2. **Fraud Ring Detection** (Community Detection)
- Community structure analysis
- Suspicious isolated clusters
- Potential Sybil attack rings

### 3. **Risk Assessment** (Trust Path Analysis)
- Shortest path to gold standard users
- Trust score along path
- Risk level classification

### 4. **Visualization Export**
- `bitcoin_trust_network.gexf` file for Gephi
- Node attributes: PageRank, community, degrees
- Edge attributes: rating, class, weight

---

##  Key Files

| File | Purpose |
|------|---------|
| `crypto_trust_analysis.ipynb` | **Main notebook** - Run this! |
| `requirements.txt` | Python dependencies |
| `validate_data.py` | Dataset validator |
| `setup.sh` | Automated setup script |
| `README.md` | Full documentation |
| `soc-sign-bitcoinotc.csv` | Dataset (included) |

---

## 🎯 Expected Results

- **Dataset**: 35,592 edges, 5,881 users
- **Positive ratings**: 90% (trust-dominated network)
- **Communities**: Multiple clusters detected
- **Execution time**: ~30 seconds for full analysis

---

## 💡 Tips

1. **First time?** Run `validate_data.py` to confirm dataset is ready
2. **Need help?** Check `README.md` for detailed documentation
3. **Visualize?** Import `bitcoin_trust_network.gexf` into Gephi
4. **Customize?** All parameters are easily adjustable in the notebook

---

## ✅ Success Criteria

You should see:
- ✅ J-curve rating distribution plot
- ✅ Top 10 trust anchors with scores
- ✅ Community detection results
- ✅ Trust path analysis with risk assessment
- ✅ GEXF file exported successfully

---

## 🆘 Troubleshooting

**Import errors?**
```bash
pip install --upgrade networkx pandas numpy matplotlib seaborn python-louvain
```

**Dataset not found?**
- File is included: `soc-sign-bitcoinotc.csv`
- If missing, extract from: `soc-sign-bitcoinotc.csv.gz`

**Jupyter not opening?**
```bash
pip install jupyter notebook
jupyter notebook
```

---

## 📚 Next Steps

1. ✅ Run the notebook
2. 📊 Review the visualizations
3. 🎨 Open GEXF in Gephi for advanced visualization
4. 🔍 Customize analysis parameters
5. 🚀 Apply to your own network data!
