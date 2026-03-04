from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class DiffStats(BaseModel):
    rows_added: int = 0
    rows_removed: int = 0
    cells_modified: int = 0
    total_rows_file1: int = 0
    total_rows_file2: int = 0

class DiffResult(BaseModel):
    stats: DiffStats
    file1_data: List[Dict[str, Any]]
    file2_data: List[Dict[str, Any]]
    file1_highlights: Dict[int, List[str]] # row_index: [columns]
    file2_highlights: Dict[int, List[str]]
    row_mapping: Dict[str, Any] # Maps keys to their status (match, added, removed)
    summary: Optional[str] = None
    column_names: List[str] = []
