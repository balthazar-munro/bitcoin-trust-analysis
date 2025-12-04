"""
Quick Dataset Validator for Crypto-Trust Project

This script validates the Bitcoin OTC dataset before running the main analysis.
"""

import pandas as pd
import os

def validate_dataset(filepath='soc-sign-bitcoinotc.csv'):
    """Validate the Bitcoin OTC dataset structure and content."""
    
    print("=" * 60)
    print("DATASET VALIDATION")
    print("=" * 60)
    
    # Check file exists
    if not os.path.exists(filepath):
        print(f"❌ ERROR: Dataset not found at {filepath}")
        print("\nPlease download from: https://snap.stanford.edu/data/soc-sign-bitcoin-otc.html")
        return False
    
    print(f"✓ File found: {filepath}")
    file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
    print(f"  File size: {file_size:.2f} MB")
    
    # Load dataset
    try:
        df = pd.read_csv(filepath, names=['source', 'target', 'rating', 'time'])
        print(f"✓ Dataset loaded successfully")
        print(f"  Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    except Exception as e:
        print(f"❌ ERROR loading dataset: {e}")
        return False
    
    # Validate schema
    print("\n--- Schema Validation ---")
    expected_cols = ['source', 'target', 'rating', 'time']
    if list(df.columns) == expected_cols:
        print(f"✓ Columns correct: {expected_cols}")
    else:
        print(f"❌ Column mismatch. Expected: {expected_cols}, Got: {list(df.columns)}")
        return False
    
    # Validate data types
    if df['source'].dtype in ['int64', 'int32'] and df['target'].dtype in ['int64', 'int32']:
        print(f"✓ User IDs are integers")
    else:
        print(f"⚠ Warning: User IDs may not be integers")
    
    # Validate rating range
    min_rating, max_rating = df['rating'].min(), df['rating'].max()
    print(f"\n--- Data Quality ---")
    print(f"Rating range: [{min_rating}, {max_rating}]")
    
    if min_rating >= -10 and max_rating <= 10:
        print(f"✓ Ratings within expected range [-10, +10]")
    else:
        print(f"⚠ Warning: Ratings outside expected range")
    
    # Check for missing values
    missing = df.isnull().sum().sum()
    if missing == 0:
        print(f"✓ No missing values")
    else:
        print(f"⚠ Warning: {missing} missing values detected")
    
    # Summary statistics
    print(f"\n--- Summary Statistics ---")
    print(f"Unique users (source): {df['source'].nunique():,}")
    print(f"Unique users (target): {df['target'].nunique():,}")
    print(f"Unique users (total): {len(set(df['source']) | set(df['target'])):,}")
    print(f"Positive ratings: {(df['rating'] > 0).sum():,} ({(df['rating'] > 0).sum()/len(df)*100:.1f}%)")
    print(f"Negative ratings: {(df['rating'] < 0).sum():,} ({(df['rating'] < 0).sum()/len(df)*100:.1f}%)")
    print(f"Neutral ratings: {(df['rating'] == 0).sum():,} ({(df['rating'] == 0).sum()/len(df)*100:.1f}%)")
    
    print("\n" + "=" * 60)
    print("✅ VALIDATION PASSED - Dataset is ready for analysis!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    validate_dataset()
