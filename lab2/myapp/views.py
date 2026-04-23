from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Category, Post, Comment, ProductCategory, Product, UserProfile
from .forms import PostForm, CommentForm, UserProfileForm


def home(request):
    categories = Category.objects.annotate(posts_total=Count("posts", distinct=True)).order_by("name")
    posts = Post.objects.select_related("category").annotate(
        comments_total=Count("comments", distinct=True)
    ).order_by("-created_at")

    selected_category_id = request.GET.get("category")

    if selected_category_id and selected_category_id.isdigit():
        posts = posts.filter(category_id=int(selected_category_id))
        selected_category_id = int(selected_category_id)
    else:
        selected_category_id = None

    context = {
        "title": "UNIChat Forum",
        "categories": categories,
        "posts": posts,
        "selected_category_id": selected_category_id,
    }
    return render(request, "myapp/home.html", context)


def category_posts(request, category_id):
    categories = Category.objects.annotate(posts_total=Count("posts", distinct=True)).order_by("name")
    category = get_object_or_404(Category, id=category_id)
    posts = Post.objects.select_related("category").annotate(
        comments_total=Count("comments", distinct=True)
    ).filter(category=category).order_by("-created_at")

    context = {
        "title": category.name,
        "categories": categories,
        "category": category,
        "posts": posts,
        "selected_category_id": category.id,
    }
    return render(request, "myapp/category_posts.html", context)


def post_detail(request, post_id):
    if not request.user.is_authenticated:
        return redirect("register")

    categories = Category.objects.annotate(posts_total=Count("posts", distinct=True)).order_by("name")
    post = get_object_or_404(Post.objects.select_related("category"), id=post_id)
    comments = Comment.objects.filter(post=post).order_by("created_at")

    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            return redirect("post_detail", post_id=post.id)
    else:
        comment_form = CommentForm()

    context = {
        "title": post.title,
        "categories": categories,
        "post": post,
        "comments": comments,
        "comment_form": comment_form,
        "selected_category_id": post.category.id,
    }
    return render(request, "myapp/post_detail.html", context)


def create_post(request):
    if not request.user.is_authenticated:
        return redirect("register")

    categories = Category.objects.annotate(posts_total=Count("posts", distinct=True)).order_by("name")

    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save()
            return redirect("post_detail", post_id=post.id)
    else:
        form = PostForm()

    context = {
        "title": "Створити тему",
        "categories": categories,
        "form": form,
        "selected_category_id": None,
    }
    return render(request, "myapp/create_post.html", context)


def register_view(request):
    categories = Category.objects.annotate(posts_total=Count("posts", distinct=True)).order_by("name")

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()

    context = {
        "title": "Реєстрація",
        "categories": categories,
        "form": form,
        "selected_category_id": None,
    }
    return render(request, "myapp/register.html", context)


def logout_view(request):
    logout(request)
    return redirect("home")


def profile_view(request):
    categories = Category.objects.annotate(posts_total=Count("posts", distinct=True)).order_by("name")
    plus_product = Product.objects.filter(unlocks_plus=True).first()

    profile = None
    form = None

    if request.user.is_authenticated:
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        if request.method == "POST" and profile.is_plus:
            form = UserProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                return redirect("profile")
        else:
            form = UserProfileForm(instance=profile)

    context = {
        "title": "My Profile",
        "categories": categories,
        "selected_category_id": None,
        "profile": profile,
        "form": form,
        "plus_product": plus_product,
    }
    return render(request, "myapp/profile.html", context)


def store_home(request):
    categories = Category.objects.annotate(posts_total=Count("posts", distinct=True)).order_by("name")
    product_categories = ProductCategory.objects.annotate(
        products_total=Count("products", distinct=True)
    ).order_by("name")
    products = Product.objects.select_related("category").order_by("name")

    context = {
        "title": "UNIChat Plus Store",
        "categories": categories,
        "selected_category_id": None,
        "product_categories": product_categories,
        "products": products,
    }
    return render(request, "myapp/store_home.html", context)


def product_category_detail(request, category_id):
    categories = Category.objects.annotate(posts_total=Count("posts", distinct=True)).order_by("name")
    product_category = get_object_or_404(ProductCategory, id=category_id)
    products = Product.objects.filter(category=product_category).order_by("name")

    context = {
        "title": product_category.name,
        "categories": categories,
        "selected_category_id": None,
        "product_category": product_category,
        "products": products,
    }
    return render(request, "myapp/product_category.html", context)


def product_detail(request, product_id):
    categories = Category.objects.annotate(posts_total=Count("posts", distinct=True)).order_by("name")
    product = get_object_or_404(Product.objects.select_related("category"), id=product_id)

    context = {
        "title": product.name,
        "categories": categories,
        "selected_category_id": None,
        "product": product,
    }
    return render(request, "myapp/product_detail.html", context)


def buy_product(request, product_id):
    if not request.user.is_authenticated:
        return redirect("register")

    product = get_object_or_404(Product, id=product_id)
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if product.unlocks_plus:
        profile.is_plus = True
        profile.plus_plan = product.name
        profile.save()

    return redirect("profile")