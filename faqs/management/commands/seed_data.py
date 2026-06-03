from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Role, UserProfile
from community.models import Badge
from faqs.models import Category, ContentStatus, FAQ


class Command(BaseCommand):
    help = 'Seed categories, sample FAQs, badges, and demo users'

    def handle(self, *args, **options):
        categories = [
            ('Academics', 'bi-book', 'Courses, exams, and academic policies'),
            ('Technical Support', 'bi-pc-display', 'IT, portals, and software issues'),
            ('Placements', 'bi-briefcase', 'Internships, jobs, and career services'),
            ('Hostel', 'bi-house', 'Accommodation and hostel rules'),
            ('Administration', 'bi-building', 'Official procedures and documents'),
            ('General Queries', 'bi-question-circle', 'Miscellaneous questions'),
        ]
        for name, icon, desc in categories:
            Category.objects.get_or_create(name=name, defaults={'icon': icon, 'description': desc})

        badges = [
            ('First Contribution', 'first-contribution', 'Posted your first FAQ', 0),
            ('Top Contributor', 'top-contributor', 'Reached 500 reputation', 500),
            ('FAQ Expert', 'faq-expert', 'Published 10 FAQs', 100),
            ('100 Upvotes', '100-upvotes', 'Received 100 upvotes', 0),
            ('Community Helper', 'community-helper', 'Helped 50 users with answers', 200),
        ]
        for name, slug, desc, threshold in badges:
            Badge.objects.get_or_create(slug=slug, defaults={
                'name': name, 'description': desc, 'threshold': threshold,
            })

        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True},
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
        profile, _ = UserProfile.objects.get_or_create(user=admin_user)
        profile.role = Role.ADMIN
        profile.save()

        mod_user, created = User.objects.get_or_create(
            username='moderator',
            defaults={'email': 'mod@example.com'},
        )
        if created:
            mod_user.set_password('mod123')
            mod_user.save()
        mp, _ = UserProfile.objects.get_or_create(user=mod_user)
        mp.role = Role.MODERATOR
        mp.save()

        demo, created = User.objects.get_or_create(username='demo', defaults={'email': 'demo@example.com'})
        if created:
            demo.set_password('demo123')
            demo.save()

        academics = Category.objects.get(name='Academics')
        placements = Category.objects.get(name='Placements')
        samples = [
            (academics, 'How do I register for courses?',
             'Use the student portal during the registration window each semester.'),
            (placements, 'Can I take leave during internship?',
             'Leave requests during internship are approved only under exceptional circumstances with prior written approval.'),
            (Category.objects.get(name='Technical Support'), 'How do I reset my password?',
             'Click Forgot Password on the login page and follow the email instructions.'),
        ]
        for cat, title, answer in samples:
            FAQ.objects.get_or_create(
                title=title,
                defaults={
                    'question': title,
                    'answer': f'<p>{answer}</p>',
                    'category': cat,
                    'author': admin_user,
                    'status': ContentStatus.PUBLISHED,
                    'published_at': timezone.now(),
                },
            )

        self.stdout.write(self.style.SUCCESS('Seed data created. Users: admin/admin123, moderator/mod123, demo/demo123'))
