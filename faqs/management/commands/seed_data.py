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
            ('Internship', 'bi-journal-code', 'Internship programs, projects, and mentorship'),
            ('Yaksha AI', 'bi-robot', 'Yaksha AI assistant features and usage'),
            ('Spurti Points', 'bi-star', 'Reward points, leaderboards, and badges'),
            ('Community & Platform', 'bi-people', 'Community contributions and platform features'),
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

        # ── Internship FAQs (1–20) ──────────────────────────────────
        internship = Category.objects.get(name='Internship')
        internship_faqs = [
            ('What is the internship duration?',
             'The internship duration depends on the selected program and is communicated during onboarding.'),
            ('How are internship projects assigned?',
             'Projects are assigned based on your skills, interests, and mentor requirements.'),
            ('Will I receive an internship certificate?',
             'Yes, eligible interns receive a certificate after successfully completing the internship requirements.'),
            ('How can I track my internship progress?',
             'Progress can be tracked through assigned tasks, mentor feedback, and project submissions.'),
            ('Can I change my project after joining?',
             'Project changes may be allowed with mentor approval and project availability.'),
            ('What happens if I miss a project deadline?',
             'Missing deadlines may affect your performance evaluation and internship completion status.'),
            ('Do I need to submit regular progress reports?',
             'Some internship programs require periodic progress reports to monitor learning and project development.'),
            ('How are mentors assigned?',
             'Mentors are assigned according to project requirements and domain expertise.'),
            ('Can I participate in multiple internship programs?',
             'Yes, provided you meet the eligibility criteria and available opportunities.'),
            ('How is internship performance evaluated?',
             'Performance is evaluated based on project quality, consistency, participation, and mentor feedback.'),
            ('I have completed my application. What should I do next?',
             'Wait for further communication regarding screening, mentor allocation, or project assignment.'),
            ('Can I work on my own project idea during the internship?',
             'Personal project proposals may be considered if they align with program objectives.'),
            ('What happens if my mentor is unavailable?',
             'The program team may assign temporary guidance or an alternative mentor.'),
            ('Will my internship be extended if my project is incomplete?',
             'Extensions are subject to mentor recommendation and program policies.'),
            ('Can I collaborate with other interns?',
             'Yes, collaboration is encouraged when it benefits the project.'),
            ('How much time should I dedicate weekly to the internship?',
             'Expected commitment varies by project and mentor expectations.'),
            ('What should I do if I am stuck on a task?',
             'Consult your mentor, project resources, or Yaksha AI for guidance.'),
            ('Will I receive feedback during the internship?',
             'Yes, mentors may provide regular feedback on your progress and performance.'),
            ('Can I switch domains after selection?',
             'Domain changes depend on availability and approval from the program team.'),
            ('What makes an intern successful in the program?',
             'Consistent effort, active participation, and timely completion of assigned tasks.'),
        ]
        for title, answer in internship_faqs:
            FAQ.objects.get_or_create(
                title=title,
                defaults={
                    'question': title,
                    'answer': f'<p>{answer}</p>',
                    'category': internship,
                    'author': admin_user,
                    'status': ContentStatus.PUBLISHED,
                    'published_at': timezone.now(),
                },
            )

        # ── Yaksha AI FAQs (21–40) ──────────────────────────────────
        yaksha_ai = Category.objects.get(name='Yaksha AI')
        yaksha_ai_faqs = [
            ('What is Yaksha AI?',
             'Yaksha AI is an intelligent assistant that helps users find answers, FAQs, and internship-related information.'),
            ('How does Yaksha AI answer questions?',
             'Yaksha AI searches the knowledge base and retrieves the most relevant information for your query.'),
            ('Can Yaksha AI answer internship-related questions?',
             'Yes, Yaksha AI can assist with internship guidelines, procedures, and common queries.'),
            ('Is Yaksha AI available 24/7?',
             'Yes, Yaksha AI is available anytime to assist users.'),
            ('Does Yaksha AI provide sources for answers?',
             'Yes, Yaksha AI can reference relevant FAQs used to generate responses.'),
            ('Can I ask follow-up questions to Yaksha AI?',
             'Yes, Yaksha AI supports follow-up questions related to previous queries.'),
            ('What should I do if Yaksha AI gives an incorrect answer?',
             'You can report the response so it can be reviewed and improved.'),
            ('Can Yaksha AI recommend related FAQs?',
             'Yes, Yaksha AI can suggest similar FAQs based on your query.'),
            ('Can Yaksha AI help new users navigate the platform?',
             'Yes, it can guide users to relevant sections, resources, and features.'),
            ('How can I help improve Yaksha AI responses?',
             'Contributing accurate FAQs and reporting incorrect answers helps improve response quality.'),
            ('Why did Yaksha AI give a different answer than I expected?',
             'Yaksha AI generates responses based on available information and query interpretation.'),
            ('Can Yaksha AI explain technical concepts?',
             'Yes, Yaksha AI can provide simplified explanations for many technical topics.'),
            ('Can Yaksha AI help me prepare for interviews?',
             'It can provide guidance, resources, and commonly asked interview questions.'),
            ('Does Yaksha AI remember my previous questions?',
             'Session behavior depends on the platform configuration and privacy settings.'),
            ('Can Yaksha AI recommend learning resources?',
             'Yes, it may suggest relevant resources based on your query.'),
            ('Why does Yaksha AI sometimes provide multiple answers?',
             'Multiple relevant FAQs may exist for a similar question.'),
            ('Can Yaksha AI help me find opportunities matching my skills?',
             'It can guide you toward relevant programs and opportunities.'),
            ('How can I ask better questions to Yaksha AI?',
             'Clear and specific questions generally produce better responses.'),
            ('Can Yaksha AI understand abbreviations and short forms?',
             'Yes, it can recognize many commonly used abbreviations.'),
            ('What happens when Yaksha AI cannot find an answer?',
             'It may suggest related FAQs or recommend contacting support.'),
        ]
        for title, answer in yaksha_ai_faqs:
            FAQ.objects.get_or_create(
                title=title,
                defaults={
                    'question': title,
                    'answer': f'<p>{answer}</p>',
                    'category': yaksha_ai,
                    'author': admin_user,
                    'status': ContentStatus.PUBLISHED,
                    'published_at': timezone.now(),
                },
            )

        # ── Spurti Points FAQs (41–60) ──────────────────────────────
        spurti_points = Category.objects.get(name='Spurti Points')
        spurti_points_faqs = [
            ('What are Spurti Points?',
             'Spurti Points are reward points earned through active participation and valuable contributions on the platform.'),
            ('How can I earn Spurti Points?',
             'Points are earned by submitting FAQs, answering questions, receiving upvotes, and contributing approved edits.'),
            ('Do approved FAQs earn Spurti Points?',
             'Yes, users receive points when their FAQs are approved and published.'),
            ('Do accepted answers provide additional Spurti Points?',
             'Yes, accepted answers may earn bonus points.'),
            ('Can I earn Spurti Points by suggesting FAQ edits?',
             'Yes, approved edit suggestions are rewarded with Spurti Points.'),
            ('Where can I view my Spurti Points?',
             'Your current point balance is displayed on your profile dashboard.'),
            ('Can I lose Spurti Points?',
             'Points may be adjusted if content violates platform guidelines or is removed.'),
            ('Are Spurti Points shown on the leaderboard?',
             'Yes, leaderboard rankings are based on accumulated points and contributions.'),
            ('Can Spurti Points unlock badges?',
             'Yes, users may earn badges after reaching specific contribution milestones.'),
            ('What is the benefit of earning more Spurti Points?',
             'Higher points improve your reputation and recognition within the community.'),
            ('Why didn\'t I receive Spurti Points for my contribution?',
             'Points may be awarded only after moderation or approval of the contribution.'),
            ('Do all activities earn Spurti Points?',
             'No, only eligible actions defined by the platform reward system earn points.'),
            ('Which activity earns the highest Spurti Points?',
             'Point values depend on the contribution type and platform settings.'),
            ('Can two users receive points for the same FAQ?',
             'Yes, if both contribute meaningfully through creation or approved edits.'),
            ('Do points expire?',
             'No, earned points remain associated with your account unless platform policies change.'),
            ('Can I see how I earned my points?',
             'Point history may be available through reputation or activity logs.'),
            ('What happens if my approved FAQ is later removed?',
             'Point adjustments may occur based on moderation decisions.'),
            ('Do moderators appear on the Spurti leaderboard?',
             'Yes, moderators may appear if they participate in community activities.'),
            ('Is there a maximum number of Spurti Points I can earn?',
             'No, users can continue earning points through ongoing contributions.'),
            ('How can I move up on the leaderboard faster?',
             'Contribute quality content consistently and engage positively with the community.'),
        ]
        for title, answer in spurti_points_faqs:
            FAQ.objects.get_or_create(
                title=title,
                defaults={
                    'question': title,
                    'answer': f'<p>{answer}</p>',
                    'category': spurti_points,
                    'author': admin_user,
                    'status': ContentStatus.PUBLISHED,
                    'published_at': timezone.now(),
                },
            )

        # ── Community & Platform FAQs (61–70) ───────────────────────
        community = Category.objects.get(name='Community & Platform')
        community_faqs = [
            ('How can I contribute to the knowledge base?',
             'Submit FAQs, answer questions, and suggest improvements to existing content.'),
            ('Can I suggest edits to an existing FAQ?',
             'Yes, edit suggestions are reviewed by moderators before being published.'),
            ('Why is my FAQ not visible after submission?',
             'Newly submitted FAQs remain in pending status until approved by a moderator.'),
            ('How long does FAQ approval take?',
             'Approval times depend on moderator availability and review workload.'),
            ('How can I report incorrect information?',
             'Use the report option available on FAQs and community content.'),
            ('What happens after I report content?',
             'Moderators review the report and take appropriate action if necessary.'),
            ('How do I bookmark useful FAQs?',
             'Click the bookmark icon on any FAQ to save it for future reference.'),
            ('Are my bookmarks visible to other users?',
             'No, bookmarks are private and only visible to your account.'),
            ('What are trending FAQs?',
             'Trending FAQs are frequently viewed, searched, or discussed by users.'),
            ('How are top contributors recognized?',
             'Top contributors are highlighted through badges, leaderboards, and reputation rankings.'),
        ]
        for title, answer in community_faqs:
            FAQ.objects.get_or_create(
                title=title,
                defaults={
                    'question': title,
                    'answer': f'<p>{answer}</p>',
                    'category': community,
                    'author': admin_user,
                    'status': ContentStatus.PUBLISHED,
                    'published_at': timezone.now(),
                },
            )

        self.stdout.write(self.style.SUCCESS(
            'Seed data created. Users: admin/admin123, moderator/mod123, demo/demo123. '
            'Added 70 FAQs across Internship, Yaksha AI, Spurti Points, and Community & Platform categories.'
        ))
