from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

class Blog(models.Model):
    CATEGORY_CHOICES = [
        ('guides', 'Educational & Learning Guides'),
        ('career', 'Career & Industry Articles'),
        ('success', 'Student Success Stories'),
        ('tips', 'Study Tips & Motivation'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='guides')
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    tags = models.CharField(max_length=100, blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
