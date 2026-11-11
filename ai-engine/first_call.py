import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

completion = client.chat.completions.create(
    model="qwen/qwen3.8-27b",
    messages=[
        {"role": "system", "content": "Tum FoodOps ke friendly assistant ho. Hinglish mein chhota jawab do."},
        {"role": "user", "content": "Kuch spicy aur veg suggest karo, 300 rupaye se kam."}
    ],
    temperature=0.2,
    max_tokens=300
)

print(completion.choices[0].message.content)