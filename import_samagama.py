import os
import django
from bs4 import BeautifulSoup

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from faqs.models import Category, FAQ, ContentStatus
from django.contrib.auth.models import User
from django.utils import timezone

file_path = r"C:\Users\ASUS\.gemini\antigravity-ide\brain\05e16666-2405-4dfb-b33d-2e64bd49f607\.system_generated\steps\15\content.md"

def import_faqs():
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')

    admin_user = User.objects.get(username='admin')
    current_category, _ = Category.objects.get_or_create(name="General Queries")

    count = 0
    # Find all h2 and details tags in order
    for element in soup.find_all(['h2', 'details']):
        if element.name == 'h2' and element.get('id', '').startswith('s-'):
            # "1. About the internship §" -> "About the internship"
            text = element.get_text(strip=True)
            if '.' in text:
                cat_text = text.split('.', 1)[-1].split('§')[0].strip()
            else:
                cat_text = text.split('§')[0].strip()
            current_category, _ = Category.objects.get_or_create(
                name=cat_text, 
                defaults={'description': cat_text}
            )
            
        elif element.name == 'details' and 'faq-q' in element.get('class', []):
            summary = element.find('summary')
            if summary:
                title_raw = summary.get_text(strip=True)
                title = title_raw.split(' ', 1)[-1].split('§')[0].strip()
                
                answer_parts = []
                for sibling in summary.find_next_siblings():
                    answer_parts.append(str(sibling))
                answer_html = "".join(answer_parts)
                
                _, created = FAQ.objects.get_or_create(
                    title=title,
                    defaults={
                        'question': title,
                        'answer': answer_html,
                        'category': current_category,
                        'author': admin_user,
                        'status': ContentStatus.PUBLISHED,
                        'published_at': timezone.now(),
                    }
                )
                if created:
                    count += 1

    print(f"Successfully imported {count} new FAQs!")

if __name__ == "__main__":
    import_faqs()
