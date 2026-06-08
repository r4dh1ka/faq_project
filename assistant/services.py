import json
from django.conf import settings
from django.db.models import Q

from faqs.models import FAQ, ContentStatus
from faqs.search import find_similar_faqs


def retrieve_faq_context(query: str, limit: int = 5) -> list[dict]:
    """Keyword + similarity retrieval from published FAQs."""
    similar = find_similar_faqs(query, limit=limit, threshold=0.35)
    keyword = FAQ.objects.filter(
        status=ContentStatus.PUBLISHED,
    ).filter(
        Q(title__icontains=query) | Q(question__icontains=query) | Q(answer__icontains=query)
    )[:limit]
    seen = set()
    results = []
    for faq in list(similar) + list(keyword):
        if faq.pk in seen:
            continue
        seen.add(faq.pk)
        results.append({
            'id': faq.pk,
            'title': faq.title,
            'question': faq.question,
            'answer': faq.answer[:1500],
            'url': faq.get_absolute_url(),
            'category': faq.category.name if faq.category else 'General',
        })
        if len(results) >= limit:
            break
    return results


def extract_formal_intent(query: str) -> str:
    # --- DEMO FALLBACK: Hardcoded translations for localhost testing ---
    q_lower = query.lower()
    if "registration ka kya seen hai" in q_lower:
        return "register"
    if "canteen" in q_lower or "khana" in q_lower or "food" in q_lower:
        return "cafeteria"
    if "midsem" in q_lower or "exam" in q_lower:
        return "examination"
    if "hostel ka wifi" in q_lower or "wifi dead" in q_lower:
        return "network"
    # ------------------------------------------------------------------

    if not getattr(settings, 'GEMINI_API_KEY', None):
        return query
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=settings.GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash')

        prompt = f"""You are a translator for a university FAQ system.
The user might type in Hinglish, GenZ slang, or casual English.
Translate their query into a short, formal English search query (maximum 5-7 words).
Only return the translated search query, nothing else.

User query: {query}"""
        response = client.chat.completions.create(
            model=model_name,
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=20,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return query


def generate_ai_response(user_message: str) -> dict:
    formal_intent = extract_formal_intent(user_message)
    context = retrieve_faq_context(formal_intent)
    sources = [{'title': c['title'], 'url': c['url']} for c in context]

    if getattr(settings, 'GEMINI_API_KEY', None):
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=settings.GEMINI_API_KEY,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
            model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash')
        
            context_text = '\n\n'.join(
                f"FAQ: {c['title']}\nQ: {c['question']}\nA: {c['answer']}" for c in context
            ) or 'No matching FAQs in database.'
            prompt = f"""You are Yaksha, an FAQ assistant for a crowdsourced knowledge platform.
Answer using ONLY the FAQ context below. Cite FAQ titles when relevant.
If the context does not contain the answer, say so and suggest browsing or asking the community.

CRITICAL TONE AND LANGUAGE MATCHING INSTRUCTION:
1. Detect the exact language of the user's question (e.g., Hindi, Marathi, Spanish, English, etc.).
2. You MUST translate your final answer into the EXACT SAME language they used.
3. Analyze the tone of their question. If they use slang, Hinglish, or casual phrasing, match their exact tone and slang in your translated response. If formal, remain formal.

FAQ Context:
{context_text}

User question: {user_message}
"""
            response = client.chat.completions.create(
                model=model_name,
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=2000,
            )
            reply = response.choices[0].message.content.strip()
            return {'reply': reply, 'sources': sources, 'suggested': _suggested_questions(context)}
        except Exception:
            pass

    return _keyword_fallback(user_message, context, sources)


def _keyword_fallback(user_message: str, context: list, sources: list) -> dict:
    if context:
        best = context[0]
        reply = (
            f"My AI brain is currently resting 💤, but I found this! According to FAQ \"{best['title']}\" ({best['category']}): "
            f"{best['answer'][:400]}{'...' if len(best['answer']) > 400 else ''}"
        )
    else:
        reply = (
            "My AI brain is currently resting 💤, and I couldn't find a matching FAQ for that right now. "
            "Try rephrasing your question, browse categories, or post a new question to the community!"
        )
    return {
        'reply': reply,
        'sources': sources,
        'suggested': _suggested_questions(context),
    }


def _suggested_questions(context: list) -> list[str]:
    if not context:
        return [
            'How do I reset my password?',
            'Where can I find placement information?',
            'How does the reputation system work?',
        ]
    return [c['title'] for c in context[:3]]
