from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from taggit.managers import TaggableManager


class ContentStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    PENDING = 'pending', 'Pending Review'
    PUBLISHED = 'published', 'Published'
    REJECTED = 'rejected', 'Rejected'


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Bootstrap icon class, e.g. bi-book')

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('faqs:category', kwargs={'slug': self.slug})

    @property
    def faq_count(self):
        return self.faqs.filter(status=ContentStatus.PUBLISHED).count()


class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'subcategories'
        ordering = ['order', 'name']
        unique_together = ('category', 'slug')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.category.name} › {self.name}'

    def get_absolute_url(self):
        return reverse('faqs:subcategory', kwargs={
            'category_slug': self.category.slug,
            'slug': self.slug,
        })


class FAQ(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    question = models.TextField()
    answer = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='faqs')
    subcategory = models.ForeignKey(
        'Subcategory', on_delete=models.SET_NULL, null=True, blank=True, related_name='faqs'
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='faqs')
    status = models.CharField(max_length=20, choices=ContentStatus.choices, default=ContentStatus.PENDING)
    tags = TaggableManager(blank=True)
    attachment = models.FileField(upload_to='faq_attachments/', blank=True, null=True)
    image = models.ImageField(upload_to='faq_images/', blank=True, null=True)
    view_count = models.PositiveIntegerField(default=0)
    upvote_count = models.PositiveIntegerField(default=0)
    downvote_count = models.PositiveIntegerField(default=0)
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200] or 'faq'
            slug = base
            n = 1
            while FAQ.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('faqs:detail', kwargs={'slug': self.slug})

    @property
    def score(self):
        return self.upvote_count - self.downvote_count


class FAQEditSuggestion(models.Model):
    faq = models.ForeignKey(FAQ, on_delete=models.CASCADE, related_name='edit_suggestions')
    suggested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True)
    question = models.TextField(blank=True)
    answer = models.TextField()
    status = models.CharField(max_length=20, choices=ContentStatus.choices, default=ContentStatus.PENDING)
    reviewer_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Edit for {self.faq.title} by {self.suggested_by.username}'


class FAQVote(models.Model):
    class VoteType(models.IntegerChoices):
        UP = 1, 'Upvote'
        DOWN = -1, 'Downvote'

    faq = models.ForeignKey(FAQ, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vote_type = models.SmallIntegerField(choices=VoteType.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('faq', 'user')

    def __str__(self):
        return f'{self.user.username} voted {self.get_vote_type_display()} on {self.faq.title}'


class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks')
    faq = models.ForeignKey(FAQ, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'faq')
        ordering = ['-created_at']


class SearchLog(models.Model):
    query = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    results_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
