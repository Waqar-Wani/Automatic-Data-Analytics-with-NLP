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
      "content": "Hi. Reply yes only"
    }
  ]
)

print(completion.choices[0].message.content)
