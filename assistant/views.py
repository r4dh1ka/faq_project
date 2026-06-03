import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .services import generate_ai_response


def chat_widget(request):
    return render(request, 'assistant/widget.html')


@require_POST
def chat_api(request):
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
    except json.JSONDecodeError:
        message = request.POST.get('message', '').strip()

    if not message:
        return JsonResponse({'error': 'Message required'}, status=400)

    result = generate_ai_response(message)
    return JsonResponse(result)
