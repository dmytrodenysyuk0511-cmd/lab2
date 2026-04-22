from django.shortcuts import render, get_object_or_404
from .models import Category, Post, Comment


def home(request):
    categories = Category.objects.all().order_by('name')
    posts = Post.objects.select_related('category').all().order_by('-created_at')

    selected_category_id = request.GET.get('category')
    if selected_category_id:
        posts = posts.filter(category_id=selected_category_id)
        selected_category_id = int(selected_category_id)
    else:
        selected_category_id = None

    context = {
        'title': 'TechCompare UA',
        'categories': categories,
        'posts': posts,
        'selected_category_id': selected_category_id,
    }
    return render(request, 'myapp/home.html', context)


def category_posts(request, category_id):
    categories = Category.objects.all().order_by('name')
    category = get_object_or_404(Category, id=category_id)
    posts = Post.objects.filter(category=category).order_by('-created_at')

    context = {
        'title': f'Категорія: {category.name}',
        'categories': categories,
        'category': category,
        'posts': posts,
        'selected_category_id': category.id,
    }
    return render(request, 'myapp/category_posts.html', context)


def post_detail(request, post_id):
    categories = Category.objects.all().order_by('name')
    post = get_object_or_404(Post.objects.select_related('category'), id=post_id)
    comments = Comment.objects.filter(post=post).order_by('-created_at')

    context = {
        'title': post.title,
        'categories': categories,
        'post': post,
        'comments': comments,
        'selected_category_id': post.category.id,
    }
    return render(request, 'myapp/post_detail.html', context)