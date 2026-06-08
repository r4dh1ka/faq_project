import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from assistant.services import extract_formal_intent, generate_ai_response

test_queries = [
    "bhai hostel ka wifi dead hai kya karu",
    "midsems kab start honge fr",
    "canteen ka menu kya hai tbh"
]

print("--- Testing Intent Extraction ---")
for q in test_queries:
    intent = extract_formal_intent(q)
    print(f"Original: {q}")
    print(f"Formal Intent: {intent}\n")

print("--- Testing YakshaBot Tone Matching ---")
sample_msg = "bro placements ka kya scene hai fr?"
response = generate_ai_response(sample_msg)
print(f"User: {sample_msg}")
print(f"YakshaBot: {response.get('reply')}")
