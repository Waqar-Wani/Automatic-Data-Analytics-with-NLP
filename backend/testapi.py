from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

completion = client.chat.completions.create(
  extra_headers={
    "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
    "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
  },
  model="qwen/qwen3-0.6b-04-28:free",
  messages=[
    {
      "role": "user",
      "content": "HI"
    }
  ]
)

print(completion.choices[0].message.content)
