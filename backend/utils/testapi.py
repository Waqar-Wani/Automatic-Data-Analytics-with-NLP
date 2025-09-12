from openai import OpenAI

client = OpenAI(
    base_url="https://api.perplexity.ai",
    api_key="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",
)

completion = client.chat.completions.create(
    model="sonar-pro",      # For real-time, citation-backed answers
    # model="sonar-medium-online",   # If available for your plan
    messages=[
        {"role": "user", "content": "Hi. Reply yes only"}
    ],
)

print(completion.choices[0].message.content)
