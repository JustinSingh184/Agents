import httpx
import os
import json
from typing import Optional, List, Dict

class OllamaClient:
    """
    Handles communication with the local Ollama instance.
    Provides a fallback mechanism if the service is unreachable.
    """
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

    async def check_health(self) -> bool:
        """Verifies if Ollama is running and the model is available."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False

    async def generate_json(self, prompt: str) -> Optional[Dict]:
        """Sends a prompt to Ollama and expects a JSON response."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    }
                )
                if response.status_code == 200:
                    res_data = response.json()
                    # Parse the string response into JSON
                    return json.loads(res_data.get("response", "{}"))
        except Exception:
            return None
        return None

    async def get_summary(self, diff_stats: Dict) -> str:
        """Generates a plain English summary of the differences."""
        prompt = f"""
        Analyze these spreadsheet difference statistics and provide a concise, professional summary in plain English.
        Stats: {json.dumps(diff_stats)}
        Focus on the impact of these changes.
        Return JSON format: {{"summary": "your explanation here"}}
        """
        result = await self.generate_json(prompt)
        return result.get("summary", "Could not generate summary.") if result else "LLM summary unavailable."
