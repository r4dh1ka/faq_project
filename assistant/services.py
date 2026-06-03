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


def generate_ai_response(user_message: str) -> dict:
    context = retrieve_faq_context(user_message)
    sources = [{'title': c['title'], 'url': c['url']} for c in context]

    if settings.OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            context_text = '\n\n'.join(
                f"FAQ: {c['title']}\nQ: {c['question']}\nA: {c['answer']}" for c in context
            ) or 'No matching FAQs in database.'
            prompt = f"""You are Yaksha, an FAQ assistant for a crowdsourced knowledge platform.
Answer using ONLY the FAQ context below. Cite FAQ titles when relevant.
If the context does not contain the answer, say so and suggest browsing or asking the community.

FAQ Context:
{context_text}

User question: {user_message}
"""
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=500,
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
            f"According to FAQ \"{best['title']}\" ({best['category']}): "
            f"{best['answer'][:400]}{'...' if len(best['answer']) > 400 else ''}"
        )
    else:
        reply = (
            "I couldn't find a matching FAQ in our knowledge base. "
            "Try rephrasing your question, browse categories, or post a new question to the community."
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
