import requests
from prompt import get_model_price

class UsageLLM:
    def __init__(self, api_key, model, temperature=0.7, max_tokens=256):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def invoke(self, prompt):
        """prompt を渡すと content, usage, cost を返す"""

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})

        # ---- モデル価格から料金算出 ----
        prices = get_model_price(self.model)
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        cost_usd = (
            prompt_tokens * prices["input"] +
            completion_tokens * prices["output"]
        )

        usage["cost_usd"] = cost_usd

        return content, usage
