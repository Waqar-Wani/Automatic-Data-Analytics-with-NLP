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
  model="mistralai/devstral-small:free", 
  messages=[
    {
      "role": "user",
      "content": "Hi. Reply yes only"
    }
  ]
)

print(completion.choices[0].message.content)
