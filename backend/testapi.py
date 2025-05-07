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
