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
