import pandas as pd
import numpy as np
from typing import List, Dict

def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardizes a dataframe by cleaning headers and handling null values.
    """
    # Clean headers: trim whitespace
    df.columns = [str(col).strip() for col in df.columns]
    
    # Fill NaN with empty string and convert to standard types
    df = df.replace({np.nan: None})
    df = df.fillna("")
    
    # Convert all values to strings for consistent comparison
    return df.map(lambda x: str(x).strip() if x is not None else "")

async def suggest_header_mapping(headers1: List[str], headers2: List[str], llm_client) -> Dict[str, str]:
    """
    Uses LLM to suggest which columns in file 2 match columns in file 1.
    """
    if not llm_client:
        return {h: h for h in headers1 if h in headers2}
        
    prompt = f"""
    Map the headers from File 2 to File 1 based on semantic similarity.
    File 1 Headers: {headers1}
    File 2 Headers: {headers2}
    Return a JSON object where keys are File 1 headers and values are the corresponding File 2 headers.
    Example: {{"Zip Code": "Postal"}}
    """
    mapping = await llm_client.generate_json(prompt)
    return mapping if mapping else {h: h for h in headers1 if h in headers2}
