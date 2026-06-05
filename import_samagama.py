import os
import django
from bs4 import BeautifulSoup

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from faqs.models import Category, FAQ, ContentStatus
from django.contrib.auth import get_user_model
from django.utils import timezone
import sys
import os

file_path = sys.argv[1] if len(sys.argv) > 1 else 'data/content.md'

def import_faqs():
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')

    User = get_user_model()
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.filter(is_staff=True).first()
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
                
                faq_obj = FAQ.objects.filter(title=title, category=current_category).first()
                if not faq_obj:
                    FAQ.objects.create(
                        title=title,
                        question=title,
                        answer=answer_html,
                        category=current_category,
                        author=admin_user,
                        status=ContentStatus.PUBLISHED,
                        published_at=timezone.now(),
                    )
                    count += 1

    print(f"Successfully imported {count} new FAQs!")

if __name__ == "__main__":
    import_faqs()
