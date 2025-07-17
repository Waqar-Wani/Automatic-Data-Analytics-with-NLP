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
  model="mistralai/mistral-small-3.2-24b-instruct:free", 
  messages=[
    {
      "role": "user",
      "content": "Hi. Reply yes only"
    }
  ]
)

print(completion.choices[0].message.content)
