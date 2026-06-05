import random
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from faqs.data.seed_content import CATEGORY_META, all_faq_entries
from faqs.models import Category, ContentStatus, FAQ, Subcategory


class Command(BaseCommand):
    help = 'Seed 250+ realistic FAQs with categories, subcategories, tags, and engagement metrics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete existing published FAQs before seeding (keeps user-created pending items)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show how many FAQs would be created without writing to DB',
        )

    def handle(self, *args, **options):
        entries = list(all_faq_entries())
        if options['dry_run']:
            self.stdout.write(f'Would process {len(entries)} FAQ entries')
            return

        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            admin = User.objects.filter(is_staff=True).first()
        if not admin:
            admin, _ = User.objects.get_or_create(
                username='admin',
                defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True},
            )

        if options['clear']:
            deleted, _ = FAQ.objects.filter(status=ContentStatus.PUBLISHED).delete()
            self.stdout.write(self.style.WARNING(f'Removed {deleted} existing FAQ rows'))

        created = 0
        updated = 0
        subcats_created = 0

        for category_name, subcat_name, title, question, answer, tags_str in entries:
            icon, desc = CATEGORY_META.get(category_name, ('bi-folder', ''))
            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={'icon': icon, 'description': desc},
            )
            if not category.icon:
                category.icon = icon
                category.description = desc or category.description
                category.save(update_fields=['icon', 'description'])

            sub_slug = slugify(subcat_name) or 'general'
            subcategory, sub_created = Subcategory.objects.get_or_create(
                category=category,
                slug=sub_slug,
                defaults={'name': subcat_name, 'order': 0},
            )
            if sub_created:
                subcats_created += 1
            if subcategory.name != subcat_name:
                subcategory.name = subcat_name
                subcategory.save(update_fields=['name'])

            tag_list = [t.strip() for t in tags_str.split(',') if t.strip()]
            views = random.randint(45, 3200)
            upvotes = random.randint(3, max(4, views // 15))
            downvotes = random.randint(0, max(1, upvotes // 8))
            published = timezone.now() - timezone.timedelta(days=random.randint(1, 400))

            faq, was_created = FAQ.objects.get_or_create(
                title=title,
                category=category,
                defaults={
                    'question': question,
                    'answer': answer,
                    'subcategory': subcategory,
                    'author': admin,
                    'status': ContentStatus.PUBLISHED,
                    'view_count': views,
                    'upvote_count': upvotes,
                    'downvote_count': downvotes,
                    'published_at': published,
                },
            )
            if was_created:
                for tag in tag_list:
                    faq.tags.add(tag)
                created += 1
            else:
                faq.subcategory = subcategory
                faq.question = question
                faq.answer = answer
                faq.status = ContentStatus.PUBLISHED
                if not faq.view_count:
                    faq.view_count = views
                    faq.upvote_count = upvotes
                    faq.downvote_count = downvotes
                if not faq.published_at:
                    faq.published_at = published
                faq.save()
                faq.tags.clear()
                for tag in tag_list:
                    faq.tags.add(tag)
                updated += 1

        total = FAQ.objects.filter(status=ContentStatus.PUBLISHED).count()
        self.stdout.write(self.style.SUCCESS(
            f'Done: {created} created, {updated} updated, {subcats_created} new subcategories. '
            f'Total published FAQs: {total}'
        ))
