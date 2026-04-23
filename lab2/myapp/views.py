from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Sum, Avg
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import (
    Category,
    Post,
    Comment,
    ProductCategory,
    Product,
    UserProfile,
    CartItem,
    NewsletterSubscriber,
    ProductRating,
)
from .forms import (
    PostForm,
    CommentForm,
    UserProfileForm,
    NewsletterForm,
    ProductRatingForm,
)


def get_base_context(request):
    categories = Category.objects.annotate(posts_total=Count("posts", distinct=True)).order_by("name")
    cart_count = 0

    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).aggregate(total=Sum("quantity"))["total"] or 0

    return {
        "categories": categories,
        "cart_count": cart_count,
    }


def home(request):
    context = get_base_context(request)
    posts = Post.objects.select_related("category").annotate(
        comments_total=Count("comments", distinct=True)
    ).order_by("-created_at")

    selected_category_id = request.GET.get("category")

    if selected_category_id and selected_category_id.isdigit():
        posts = posts.filter(category_id=int(selected_category_id))
        selected_category_id = int(selected_category_id)
    else:
        selected_category_id = None

    context.update({
        "title": "UNIChat Forum",
        "posts": posts,
        "selected_category_id": selected_category_id,
    })
    return render(request, "myapp/home.html", context)


def category_posts(request, category_id):
    context = get_base_context(request)
    category = get_object_or_404(Category, id=category_id)
    posts = Post.objects.select_related("category").annotate(
        comments_total=Count("comments", distinct=True)
    ).filter(category=category).order_by("-created_at")

    context.update({
        "title": category.name,
        "category": category,
        "posts": posts,
        "selected_category_id": category.id,
    })
    return render(request, "myapp/category_posts.html", context)


def post_detail(request, post_id):
    if not request.user.is_authenticated:
        return redirect("register")

    context = get_base_context(request)
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

    context.update({
        "title": post.title,
        "post": post,
        "comments": comments,
        "comment_form": comment_form,
        "selected_category_id": post.category.id,
    })
    return render(request, "myapp/post_detail.html", context)


def create_post(request):
    if not request.user.is_authenticated:
        return redirect("register")

    context = get_base_context(request)

    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save()
            return redirect("post_detail", post_id=post.id)
    else:
        form = PostForm()

    context.update({
        "title": "Створити тему",
        "form": form,
        "selected_category_id": None,
    })
    return render(request, "myapp/create_post.html", context)


def register_view(request):
    context = get_base_context(request)

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

    context.update({
        "title": "Реєстрація",
        "form": form,
        "selected_category_id": None,
    })
    return render(request, "myapp/register.html", context)


def logout_view(request):
    logout(request)
    return redirect("home")


def profile_view(request):
    context = get_base_context(request)
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

    context.update({
        "title": "My Profile",
        "selected_category_id": None,
        "profile": profile,
        "form": form,
        "plus_product": plus_product,
    })
    return render(request, "myapp/profile.html", context)


def store_home(request):
    context = get_base_context(request)
    product_categories = ProductCategory.objects.annotate(
        products_total=Count("products", distinct=True)
    ).order_by("name")
    products = Product.objects.select_related("category").order_by("name")

    context.update({
        "title": "UNIChat Plus Store",
        "selected_category_id": None,
        "product_categories": product_categories,
        "products": products,
        "newsletter_form": NewsletterForm(),
    })
    return render(request, "myapp/store_home.html", context)


def product_category_detail(request, category_id):
    context = get_base_context(request)
    product_category = get_object_or_404(ProductCategory, id=category_id)
    products = Product.objects.filter(category=product_category).order_by("name")

    context.update({
        "title": product_category.name,
        "selected_category_id": None,
        "product_category": product_category,
        "products": products,
    })
    return render(request, "myapp/product_category.html", context)


def product_detail(request, product_id):
    context = get_base_context(request)
    product = get_object_or_404(Product.objects.select_related("category"), id=product_id)
    ratings = ProductRating.objects.filter(product=product).select_related("user").order_by("-updated_at")
    average_score = ratings.aggregate(avg=Avg("score"))["avg"]
    user_rating = None

    if request.user.is_authenticated:
        user_rating = ProductRating.objects.filter(user=request.user, product=product).first()

    context.update({
        "title": product.name,
        "selected_category_id": None,
        "product": product,
        "average_score": average_score,
        "ratings": ratings,
        "ratings_count": ratings.count(),
        "user_rating": user_rating,
        "rating_form": ProductRatingForm(instance=user_rating) if user_rating else ProductRatingForm(),
    })
    return render(request, "myapp/product_detail.html", context)


def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect("register")

    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={"quantity": 1},
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    next_url = request.POST.get("next")
    if next_url:
        return redirect(next_url)

    return redirect("cart_view")


def cart_view(request):
    if not request.user.is_authenticated:
        return redirect("register")

    context = get_base_context(request)
    cart_items = CartItem.objects.filter(user=request.user).select_related("product").order_by("-created_at")
    total_price = sum(item.quantity * item.product.price for item in cart_items)

    context.update({
        "title": "Кошик",
        "selected_category_id": None,
        "cart_items": cart_items,
        "total_price": total_price,
        "newsletter_form": NewsletterForm(),
    })
    return render(request, "myapp/cart.html", context)


def remove_from_cart(request, item_id):
    if not request.user.is_authenticated:
        return redirect("register")

    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    return redirect("cart_view")


def checkout_cart(request):
    if not request.user.is_authenticated:
        return redirect("register")

    cart_items = CartItem.objects.filter(user=request.user).select_related("product")
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    for item in cart_items:
        if item.product.unlocks_plus:
            profile.is_plus = True
            profile.plus_plan = item.product.name

    profile.save()
    cart_items.delete()

    return redirect("profile")


def newsletter_subscribe(request):
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]

            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=email,
                defaults={"name": name},
            )

            if not created and subscriber.name != name:
                subscriber.name = name
                subscriber.save()

    next_url = request.POST.get("next")
    if next_url:
        return redirect(next_url)

    return redirect("store_home")


def rate_product(request, product_id):
    if not request.user.is_authenticated:
        return redirect("register")

    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        form = ProductRatingForm(request.POST)
        if form.is_valid():
            ProductRating.objects.update_or_create(
                user=request.user,
                product=product,
                defaults={
                    "score": form.cleaned_data["score"],
                    "comment": form.cleaned_data["comment"],
                },
            )

    return redirect("product_detail", product_id=product.id)


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