from django.shortcuts import render, get_object_or_404
from .models import Blog

def blog_list(request):
    category = request.GET.get('category')
    blogs = Blog.objects.filter(is_published=True).order_by('-created_at')

    if category:
        blogs = blogs.filter(category=category)

    return render(request, 'blogs/blog_list.html', {'blogs': blogs})

def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug, is_published=True)
    related_blogs = Blog.objects.filter(category=blog.category, is_published=True).exclude(id=blog.id)[:3]

    return render(request, 'blogs/blog_detail.html', {
        'blog': blog,
        'related_blogs': related_blogs
    })
