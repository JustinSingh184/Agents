import pandas as pd
from typing import Dict, List, Tuple, Any
from .models import DiffResult, DiffStats

def perform_diff(df1: pd.DataFrame, df2: pd.DataFrame, row_key: str) -> DiffResult:
    """
    The core deterministic diff engine.
    Aligns rows by the selected key and compares cell by cell.
    """
    stats = DiffStats(
        total_rows_file1=len(df1),
        total_rows_file2=len(df2)
    )
    
    file1_highlights = {}
    file2_highlights = {}
    
    # Ensure row_key exists in both, otherwise fallback to index
    if row_key not in df1.columns or row_key not in df2.columns:
        df1['_key'] = df1.index.astype(str)
        df2['_key'] = df2.index.astype(str)
        actual_key = '_key'
    else:
        actual_key = row_key

    # Create lookups
    dict1 = df1.set_index(actual_key).to_dict('index')
    dict2 = df2.set_index(actual_key).to_dict('index')
    
    keys1 = set(dict1.keys())
    keys2 = set(dict2.keys())
    
    common_keys = keys1.intersection(keys2)
    removed_keys = keys1 - keys2
    added_keys = keys2 - keys1
    
    stats.rows_removed = len(removed_keys)
    stats.rows_added = len(added_keys)
    
    # Identify modified cells in common rows
    for key in common_keys:
        row1 = dict1[key]
        row2 = dict2[key]
        
        changed_cols = []
        for col in df1.columns:
            if col == actual_key: continue
            
            val1 = str(row1.get(col, ""))
            val2 = str(row2.get(col, ""))
            
            if val1 != val2:
                changed_cols.append(col)
                stats.cells_modified += 1
        
        if changed_cols:
            # Get original integer indices for highlighting
            # We use float/int to string conversion carefully if needed, 
            # but since we normalized to string, we match directly.
            idx1 = df1[df1[actual_key] == key].index[0]
            idx2 = df2[df2[actual_key] == key].index[0]
            file1_highlights[int(idx1)] = changed_cols
            file2_highlights[int(idx2)] = changed_cols

    # Highlight added/removed rows
    for key in removed_keys:
        idx_matches = df1[df1[actual_key] == key].index
        if len(idx_matches) > 0:
            idx = idx_matches[0]
            file1_highlights[int(idx)] = list(df1.columns)
        
    for key in added_keys:
        idx_matches = df2[df2[actual_key] == key].index
        if len(idx_matches) > 0:
            idx = idx_matches[0]
            file2_highlights[int(idx)] = list(df2.columns)

    return DiffResult(
        stats=stats,
        file1_data=df1.to_dict('records'),
        file2_data=df2.to_dict('records'),
        file1_highlights=file1_highlights,
        file2_highlights=file2_highlights,
        row_mapping={"added": list(added_keys), "removed": list(removed_keys)},
        column_names=list(df1.columns)
    )
