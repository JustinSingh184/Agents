import pandas as pd
from .normalization import normalize_dataframe
from .diff_engine import perform_diff
from .models import DiffResult
from llm.ollama import OllamaClient

class CompareAgent:
    """
    Orchestrates the comparison pipeline.
    Coordinates between normalization, LLM intelligence, and the diff engine.
    """
    def __init__(self):
        self.llm = OllamaClient()

    async def run(self, file1_path: str, file2_path: str, row_key: str, use_llm: bool) -> DiffResult:
        # Step 1: Load files
        df1 = self._load_file(file1_path)
        df2 = self._load_file(file2_path)
        
        # Step 2: Normalize
        df1 = normalize_dataframe(df1)
        df2 = normalize_dataframe(df2)
        
        # Step 3: Perform Diff
        result = perform_diff(df1, df2, row_key)
        
        # Step 4: Optional LLM Summary
        if use_llm:
            is_healthy = await self.llm.check_health()
            if is_healthy:
                result.summary = await self.llm.get_summary(result.stats.dict())
            else:
                result.summary = "Ollama is offline. Proceeding with deterministic diff."
        
        return result

    def _load_file(self, path: str) -> pd.DataFrame:
        if path.endswith('.csv'):
            return pd.read_csv(path)
        return pd.read_excel(path)
