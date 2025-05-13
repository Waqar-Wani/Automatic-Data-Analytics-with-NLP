import requests
import json
from openai import OpenAI

API_KEY = "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",
AI_model="qwen/qwen3-0.6b-04-28:free"
# 1. Check API key limit/status
response = requests.get(
    url="https://openrouter.ai/api/v1/auth/key",
    headers={
        "Authorization": f"Bearer {API_KEY}"
    }
)

print("API Key Status:")
print(json.dumps(response.json(), indent=2))

# 2. If key is valid, run the test API call
if response.status_code == 200 and response.json().get("rate_limit", {}).get("remaining", 1) > 0:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=API_KEY,
    )

    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
            "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
        },
        model=AI_model,
        messages=[
            {
                "role": "user",
                "content": "Hi, how are you?"
            }
        ]
    )

    print("\nTest API Call Result:")
    print(completion.choices[0].message.content)
else:
    print("\nAPI key is invalid or rate limit exceeded. Test API call not performed.")
