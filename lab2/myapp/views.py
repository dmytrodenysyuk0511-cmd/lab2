import random
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Count, Sum, Avg, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils import timezone

from .forms import (
    PostForm,
    CommentForm,
    UserProfileForm,
    NewsletterForm,
    ProductRatingForm,
    RegisterForm,
    LoginForm,
    PasswordResetRequestForm,
    PasswordResetConfirmForm,
)

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
    Order,
    OrderItem,
    PasswordResetCode,
    SavedItem,
    Friendship,
    DirectMessage,
    Notification,
)

from .i18n import get_ui_text


def get_base_context(request):
    categories = Category.objects.annotate(
        posts_total=Count("posts", distinct=True)
    ).order_by("name")

    cart_count = 0
    saved_count = 0
    notifications_count = 0

    if request.user.is_authenticated:
        cart_count = (
            CartItem.objects.filter(user=request.user).aggregate(total=Sum("quantity"))["total"]
            or 0
        )

        saved_count = SavedItem.objects.filter(user=request.user).count()
        notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()

    site_theme = request.session.get("site_theme", "light")
    site_language = request.session.get("site_language", "uk")

    if site_theme not in ["light", "dark"]:
        site_theme = "light"

    if site_language not in ["uk", "en"]:
        site_language = "uk"

    return {
        "categories": categories,
        "cart_count": cart_count,
        "saved_count": saved_count,
        "notifications_count": notifications_count,
        "site_theme": site_theme,
        "site_language": site_language,
        "ui": get_ui_text(site_language),
    }


def get_profile_media_data(profile):
    live_photo_url = ""
    live_photo_is_video = False

    if profile.live_photo_file:
        live_photo_url = profile.live_photo_file.url
        lower_url = live_photo_url.lower()
        live_photo_is_video = (
            lower_url.endswith(".mp4")
            or lower_url.endswith(".webm")
            or lower_url.endswith(".mov")
        )

    return live_photo_url, live_photo_is_video


def is_video_file(file_url):
    lower_url = file_url.lower()
    return (
        lower_url.endswith(".mp4")
        or lower_url.endswith(".webm")
        or lower_url.endswith(".mov")
        or lower_url.endswith(".quicktime")
    )


def home(request):
    context = get_base_context(request)

    categories = Category.objects.annotate(
        topics_total=Count("posts", distinct=True),
        messages_total=Count("posts__comments", distinct=True),
    ).order_by("name")

    posts = (
        Post.objects.select_related("category", "author")
        .annotate(comments_total=Count("comments", distinct=True))
        .order_by("-updated_at", "-created_at")
    )

    selected_category_id = request.GET.get("category")

    if selected_category_id and selected_category_id.isdigit():
        selected_category_id = int(selected_category_id)
        posts = posts.filter(category_id=selected_category_id)
    else:
        selected_category_id = None

    context.update(
        {
            "title": "UNIChat Forum",
            "categories": categories,
            "posts": posts,
            "latest_posts": posts,
            "recent_posts": posts,
            "selected_category_id": selected_category_id,
        }
    )

    return render(request, "myapp/home.html", context)


def category_posts(request, category_id):
    context = get_base_context(request)

    category = get_object_or_404(Category, id=category_id)

    posts = (
        Post.objects.select_related("category", "author")
        .annotate(comments_total=Count("comments", distinct=True))
        .filter(category=category)
        .order_by("-updated_at", "-created_at")
    )

    context.update(
        {
            "title": category.name,
            "category": category,
            "posts": posts,
            "selected_category_id": category.id,
        }
    )

    return render(request, "myapp/category_posts.html", context)


def post_detail(request, post_id):
    if not request.user.is_authenticated:
        return redirect("login_view")

    context = get_base_context(request)

    post = get_object_or_404(
        Post.objects.select_related("category", "author"),
        id=post_id
    )

    messages = list(
        Comment.objects.filter(post=post)
        .select_related("author", "parent", "parent__author")
        .order_by("created_at")
    )

    for message in messages:
        if message.author is None and message.author_name:
            found_user = User.objects.filter(username=message.author_name).first()

            if found_user:
                message.author = found_user
                message.save(update_fields=["author"])

    messages = list(
        Comment.objects.filter(post=post)
        .select_related("author", "parent", "parent__author")
        .order_by("created_at")
    )

    author_ids = []

    for message in messages:
        if message.author_id:
            author_ids.append(message.author_id)

        if message.parent and message.parent.author_id:
            author_ids.append(message.parent.author_id)

    profiles_by_user_id = {
        profile.user_id: profile
        for profile in UserProfile.objects.filter(user_id__in=author_ids)
    }

    saved_post_ids = []
    saved_comment_ids = []

    if request.user.is_authenticated:
        saved_post_ids = list(
            SavedItem.objects.filter(
                user=request.user,
                post__isnull=False,
            ).values_list("post_id", flat=True)
        )

        saved_comment_ids = list(
            SavedItem.objects.filter(
                user=request.user,
                comment__isnull=False,
            ).values_list("comment_id", flat=True)
        )

    message_items = []

    for message in messages:
        avatar_url = ""
        author_username = message.author_name
        author_profile_username = ""
        media_url = ""
        media_is_video = False

        if message.author:
            author_username = message.author.username
            author_profile_username = message.author.username

            profile = profiles_by_user_id.get(message.author_id)

            if profile and profile.avatar_file:
                avatar_url = profile.avatar_file.url

        if message.media_file:
            media_url = message.media_file.url
            media_is_video = is_video_file(media_url)

        parent_author_name = ""
        parent_text = ""

        if message.parent:
            if message.parent.author:
                parent_author_name = message.parent.author.username
            else:
                parent_author_name = message.parent.author_name

            parent_text = message.parent.text

        message_items.append(
            {
                "message": message,
                "avatar_url": avatar_url,
                "author_username": author_username,
                "author_profile_username": author_profile_username,
                "parent_author_name": parent_author_name,
                "parent_text": parent_text,
                "media_url": media_url,
                "media_is_video": media_is_video,
                "is_saved": message.id in saved_comment_ids,
                "is_own": message.author_id == request.user.id,
            }
        )

    if request.method == "POST":
        comment_form = CommentForm(request.POST, request.FILES)

        if comment_form.is_valid():
            parent_id = request.POST.get("parent_id")
            parent_message = None

            if parent_id and parent_id.isdigit():
                parent_message = Comment.objects.filter(
                    id=int(parent_id),
                    post=post
                ).first()

            new_message = comment_form.save(commit=False)
            new_message.post = post
            new_message.author = request.user
            new_message.author_name = request.user.username
            new_message.parent = parent_message
            new_message.save()

            post.updated_at = timezone.now()
            post.save(update_fields=["updated_at"])

            # Створити сповіщення для автора батьківського повідомлення
            if parent_message and parent_message.author and parent_message.author != request.user:
                Notification.objects.create(
                    user=parent_message.author,
                    notification_type="reply",
                    comment=new_message,
                    from_user=request.user
                )

            # Створити сповіщення для автора поста, якщо це не відповідь і не сам автор
            if not parent_message and post.author and post.author != request.user:
                Notification.objects.create(
                    user=post.author,
                    notification_type="reply",
                    comment=new_message,
                    from_user=request.user
                )

            return redirect("post_detail", post_id=post.id)
    else:
        comment_form = CommentForm()

    context.update(
        {
            "title": post.title,
            "post": post,
            "messages": messages,
            "message_items": message_items,
            "comment_form": comment_form,
            "selected_category_id": post.category.id,
            "saved_post_ids": saved_post_ids,
            "saved_comment_ids": saved_comment_ids,
        }
    )

    return render(request, "myapp/post_detail.html", context)


def create_post(request):
    if not request.user.is_authenticated:
        return redirect("login_view")

    context = get_base_context(request)

    category_id = request.GET.get("category")
    initial_data = {}

    if category_id and category_id.isdigit():
        initial_data["category"] = int(category_id)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.author_name = request.user.username
            post.save()
            return redirect("post_detail", post_id=post.id)
    else:
        form = PostForm(initial=initial_data)

    context.update(
        {
            "title": "Створити підтему",
            "form": form,
            "selected_category_id": None,
        }
    )

    return render(request, "myapp/create_post.html", context)


def register_view(request):
    context = get_base_context(request)

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"].strip().lower()
            user.save()

            UserProfile.objects.get_or_create(user=user)
            login(request, user)

            return redirect("home")
    else:
        form = RegisterForm()

    context.update(
        {
            "title": "Зареєструватись",
            "form": form,
            "selected_category_id": None,
        }
    )

    return render(request, "myapp/register.html", context)


def login_view(request):
    context = get_base_context(request)

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            login(request, form.get_user())
            return redirect("home")
    else:
        form = LoginForm()

    context.update(
        {
            "title": "Увійти",
            "form": form,
            "selected_category_id": None,
        }
    )

    return render(request, "myapp/login.html", context)


def logout_view(request):
    logout(request)
    return redirect("home")


def password_reset_request_view(request):
    context = get_base_context(request)

    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"].strip().lower()
            user = User.objects.filter(email__iexact=email).order_by("-id").first()

            if user:
                code = str(random.randint(100000, 999999))

                PasswordResetCode.objects.create(
                    user=user,
                    email=user.email,
                    code=code,
                    expires_at=timezone.now() + timedelta(minutes=15),
                )

                send_mail(
                    "UNIChat password reset code",
                    f"Твій тимчасовий код для відновлення пароля: {code}",
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )

                return redirect("password_reset_confirm_view")
    else:
        form = PasswordResetRequestForm()

    context.update(
        {
            "title": "Змінити пароль",
            "form": form,
            "selected_category_id": None,
        }
    )

    return render(request, "myapp/password_reset_request.html", context)


def password_reset_confirm_view(request):
    context = get_base_context(request)

    if request.method == "POST":
        form = PasswordResetConfirmForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"].strip().lower()
            code = form.cleaned_data["code"].strip()
            password1 = form.cleaned_data["new_password1"]
            password2 = form.cleaned_data["new_password2"]

            if password1 == password2:
                reset_code = (
                    PasswordResetCode.objects.filter(
                        email__iexact=email,
                        code=code,
                        is_used=False,
                    )
                    .order_by("-created_at")
                    .first()
                )

                if reset_code and reset_code.is_valid():
                    user = reset_code.user
                    user.set_password(password1)
                    user.save()

                    reset_code.is_used = True
                    reset_code.save()

                    return redirect("login_view")
    else:
        form = PasswordResetConfirmForm()

    context.update(
        {
            "title": "Підтвердження коду",
            "form": form,
            "selected_category_id": None,
        }
    )

    return render(request, "myapp/password_reset_confirm.html", context)


def profile_view(request):
    if not request.user.is_authenticated:
        return redirect("login_view")

    context = get_base_context(request)

    profile, created = UserProfile.objects.get_or_create(user=request.user)
    plus_product = Product.objects.filter(unlocks_plus=True).first()

    old_live_photo_file = profile.live_photo_file
    old_song_file = profile.song_file
    old_favorite_song = profile.favorite_song

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            updated_profile = form.save(commit=False)

            if not profile.is_plus:
                updated_profile.live_photo_file = old_live_photo_file
                updated_profile.song_file = old_song_file
                updated_profile.favorite_song = old_favorite_song
            else:
                if request.POST.get("clear_live_photo_file"):
                    updated_profile.live_photo_file = None

                if request.POST.get("clear_song_file"):
                    updated_profile.song_file = None

                manual_favorite_song = request.POST.get("favorite_song")

                if manual_favorite_song is not None:
                    updated_profile.favorite_song = manual_favorite_song.strip()

            if request.POST.get("clear_avatar_file"):
                updated_profile.avatar_file = None

            updated_profile.user = request.user
            updated_profile.save()

            return redirect("profile")
    else:
        form = UserProfileForm(instance=profile)

    if request.user.is_staff or request.user.is_superuser:
        orders = (
            Order.objects.select_related("user")
            .prefetch_related("items")
            .order_by("-created_at")
        )
        cabinet_title = "Всі замовлення"
    else:
        orders = (
            Order.objects.filter(user=request.user)
            .prefetch_related("items")
            .order_by("-created_at")
        )
        cabinet_title = "Мої замовлення"

    posts_count = Post.objects.filter(author=request.user).count()
    comments_count = Comment.objects.filter(author=request.user).count()
    orders_count = orders.count()
    total_spent = orders.aggregate(total=Sum("total_price"))["total"] or 0
    recent_posts = Post.objects.filter(author=request.user).order_by("-created_at")[:5]

    live_photo_url, live_photo_is_video = get_profile_media_data(profile)

    context.update(
        {
            "title": "Особистий кабінет",
            "selected_category_id": None,
            "profile": profile,
            "user_profile": profile,
            "form": form,
            "plus_product": plus_product,
            "orders": orders,
            "cabinet_title": cabinet_title,
            "posts_count": posts_count,
            "comments_count": comments_count,
            "orders_count": orders_count,
            "total_spent": total_spent,
            "recent_posts": recent_posts,
            "live_photo_url": live_photo_url,
            "live_photo_is_video": live_photo_is_video,
        }
    )

    return render(request, "myapp/profile.html", context)


def public_profile_view(request, username):
    context = get_base_context(request)

    profile_user = get_object_or_404(User, username=username)
    profile, created = UserProfile.objects.get_or_create(user=profile_user)

    friendship_status = None
    if request.user.is_authenticated and request.user != profile_user:
        friendship = Friendship.objects.filter(
            Q(from_user=request.user, to_user=profile_user) |
            Q(from_user=profile_user, to_user=request.user)
        ).first()

        if friendship:
            if friendship.status == "accepted":
                friendship_status = "accepted"
            elif friendship.from_user == request.user:
                friendship_status = "pending_sent"
            else:
                friendship_status = "pending_received"

    user_posts = Post.objects.filter(
        Q(author=profile_user) | Q(author_name=profile_user.username)
    ).distinct()

    user_comments = Comment.objects.filter(
        Q(author=profile_user) | Q(author_name=profile_user.username)
    ).distinct()

    recent_posts = (
        user_posts
        .select_related("category", "author")
        .annotate(comments_total=Count("comments", distinct=True))
        .order_by("-created_at")[:6]
    )

    live_photo_url, live_photo_is_video = get_profile_media_data(profile)

    context.update(
        {
            "title": f"Профіль {profile_user.username}",
            "profile_user": profile_user,
            "profile": profile,
            "posts_count": user_posts.count(),
            "comments_count": user_comments.count(),
            "recent_posts": recent_posts,
            "live_photo_url": live_photo_url,
            "live_photo_is_video": live_photo_is_video,
            "friendship_status": friendship_status,
        }
    )

    return render(request, "myapp/public_profile.html", context)


def account_settings_view(request):
    if not request.user.is_authenticated:
        return redirect("login_view")

    context = get_base_context(request)

    if request.method == "POST":
        theme = request.POST.get("theme", "light")
        language = request.POST.get("language", "uk")

        if theme in ["light", "dark"]:
            request.session["site_theme"] = theme

        if language in ["uk", "en"]:
            request.session["site_language"] = language

        request.session.modified = True
        return redirect("account_settings")

    selected_theme = request.session.get("site_theme", "light")
    selected_language = request.session.get("site_language", "uk")

    if selected_theme not in ["light", "dark"]:
        selected_theme = "light"

    if selected_language not in ["uk", "en"]:
        selected_language = "uk"

    title = "Settings" if selected_language == "en" else "Налаштування"

    context.update(
        {
            "title": title,
            "selected_theme": selected_theme,
            "selected_language": selected_language,
        }
    )

    return render(request, "myapp/account_settings.html", context)


def saved_items_view(request):
    if not request.user.is_authenticated:
        return redirect("login_view")

    context = get_base_context(request)

    saved_posts = (
        SavedItem.objects.filter(user=request.user, post__isnull=False)
        .select_related("post", "post__category", "post__author")
        .order_by("-created_at")
    )

    saved_comments = (
        SavedItem.objects.filter(user=request.user, comment__isnull=False)
        .select_related(
            "comment",
            "comment__post",
            "comment__post__category",
            "comment__author",
        )
        .order_by("-created_at")
    )

    context.update(
        {
            "title": "Збережене",
            "saved_posts": saved_posts,
            "saved_comments": saved_comments,
        }
    )

    return render(request, "myapp/saved_items.html", context)


def toggle_save_post(request, post_id):
    if not request.user.is_authenticated:
        return redirect("login_view")

    post = get_object_or_404(Post, id=post_id)

    saved_item = SavedItem.objects.filter(
        user=request.user,
        post=post,
        comment__isnull=True,
    ).first()

    if saved_item:
        saved_item.delete()
    else:
        SavedItem.objects.create(
            user=request.user,
            post=post,
        )

    next_url = request.POST.get("next")

    if next_url:
        return redirect(next_url)

    return redirect("post_detail", post_id=post.id)


def toggle_save_comment(request, comment_id):
    if not request.user.is_authenticated:
        return redirect("login_view")

    comment = get_object_or_404(Comment, id=comment_id)

    saved_item = SavedItem.objects.filter(
        user=request.user,
        comment=comment,
        post__isnull=True,
    ).first()

    if saved_item:
        saved_item.delete()
    else:
        SavedItem.objects.create(
            user=request.user,
            comment=comment,
        )

    next_url = request.POST.get("next")

    if next_url:
        return redirect(next_url)

    return HttpResponseRedirect(
        reverse("post_detail", args=[comment.post.id]) + f"#message-{comment.id}"
    )


def store_home(request):
    context = get_base_context(request)

    product_categories = ProductCategory.objects.annotate(
        products_total=Count("products", distinct=True)
    ).order_by("name")

    products = Product.objects.select_related("category").order_by("name")

    context.update(
        {
            "title": "UNIChat Plus Store",
            "selected_category_id": None,
            "product_categories": product_categories,
            "products": products,
            "newsletter_form": NewsletterForm(),
        }
    )

    return render(request, "myapp/store_home.html", context)


def product_category_detail(request, category_id):
    context = get_base_context(request)

    product_category = get_object_or_404(ProductCategory, id=category_id)
    products = Product.objects.filter(category=product_category).order_by("name")

    context.update(
        {
            "title": product_category.name,
            "selected_category_id": None,
            "product_category": product_category,
            "products": products,
        }
    )

    return render(request, "myapp/product_category.html", context)


def product_detail(request, product_id):
    context = get_base_context(request)

    product = get_object_or_404(Product.objects.select_related("category"), id=product_id)

    ratings = (
        ProductRating.objects.filter(product=product)
        .select_related("user")
        .order_by("-updated_at")
    )

    average_score = ratings.aggregate(avg=Avg("score"))["avg"]
    user_rating = None

    if request.user.is_authenticated:
        user_rating = ProductRating.objects.filter(
            user=request.user,
            product=product,
        ).first()

    context.update(
        {
            "title": product.name,
            "selected_category_id": None,
            "product": product,
            "average_score": average_score,
            "ratings": ratings,
            "ratings_count": ratings.count(),
            "user_rating": user_rating,
            "rating_form": ProductRatingForm(instance=user_rating)
            if user_rating
            else ProductRatingForm(),
        }
    )

    return render(request, "myapp/product_detail.html", context)


def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect("login_view")

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
        return redirect("login_view")

    context = get_base_context(request)

    cart_items = (
        CartItem.objects.filter(user=request.user)
        .select_related("product")
        .order_by("-created_at")
    )

    total_price = sum(item.quantity * item.product.price for item in cart_items)

    context.update(
        {
            "title": "Кошик",
            "selected_category_id": None,
            "cart_items": cart_items,
            "total_price": total_price,
            "newsletter_form": NewsletterForm(),
        }
    )

    return render(request, "myapp/cart.html", context)


def remove_from_cart(request, item_id):
    if not request.user.is_authenticated:
        return redirect("login_view")

    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()

    return redirect("cart_view")


def checkout_cart(request):
    if not request.user.is_authenticated:
        return redirect("login_view")

    cart_items = CartItem.objects.filter(user=request.user).select_related("product")

    if not cart_items.exists():
        return redirect("cart_view")

    total_price = sum(item.quantity * item.product.price for item in cart_items)

    order = Order.objects.create(
        user=request.user,
        total_price=total_price,
        status="completed",
    )

    profile, created = UserProfile.objects.get_or_create(user=request.user)

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name=item.product.name,
            price=item.product.price,
            quantity=item.quantity,
        )

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
        return redirect("login_view")

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
        return redirect("login_view")

    product = get_object_or_404(Product, id=product_id)
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if product.unlocks_plus:
        profile.is_plus = True
        profile.plus_plan = product.name
        profile.save()

        order = Order.objects.create(
            user=request.user,
            total_price=product.price,
            status="completed",
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            price=product.price,
            quantity=1,
        )

    return redirect("profile")


def friends_list_view(request):
    if not request.user.is_authenticated:
        return redirect("login_view")

    context = get_base_context(request)

    friends = Friendship.objects.filter(
        Q(from_user=request.user, status="accepted") |
        Q(to_user=request.user, status="accepted")
    ).select_related("from_user", "to_user")

    friend_users = []
    for friendship in friends:
        friend = friendship.to_user if friendship.from_user == request.user else friendship.from_user
        friend_users.append(friend)

    pending_requests = Friendship.objects.filter(
        to_user=request.user,
        status="pending"
    ).select_related("from_user")

    sent_requests = Friendship.objects.filter(
        from_user=request.user,
        status="pending"
    ).select_related("to_user")

    context.update({
        "title": "Друзі",
        "friend_users": friend_users,
        "pending_requests": pending_requests,
        "sent_requests": sent_requests,
    })

    return render(request, "myapp/friends_list.html", context)


def send_friend_request(request, username):
    if not request.user.is_authenticated:
        return redirect("login_view")

    to_user = get_object_or_404(User, username=username)

    if to_user == request.user:
        return redirect("friends_list")

    existing = Friendship.objects.filter(
        Q(from_user=request.user, to_user=to_user) |
        Q(from_user=to_user, to_user=request.user)
    ).first()

    if not existing:
        Friendship.objects.create(
            from_user=request.user,
            to_user=to_user,
            status="pending"
        )

    return redirect("public_profile", username=username)


def accept_friend_request(request, request_id):
    if not request.user.is_authenticated:
        return redirect("login_view")

    friendship = get_object_or_404(
        Friendship,
        id=request_id,
        to_user=request.user,
        status="pending"
    )

    friendship.status = "accepted"
    friendship.save()

    return redirect("friends_list")


def reject_friend_request(request, request_id):
    if not request.user.is_authenticated:
        return redirect("login_view")

    friendship = get_object_or_404(
        Friendship,
        id=request_id,
        to_user=request.user,
        status="pending"
    )

    friendship.delete()

    return redirect("friends_list")


def remove_friend(request, username):
    if not request.user.is_authenticated:
        return redirect("login_view")

    friend = get_object_or_404(User, username=username)

    Friendship.objects.filter(
        Q(from_user=request.user, to_user=friend) |
        Q(from_user=friend, to_user=request.user)
    ).delete()

    return redirect("friends_list")


def messages_list_view(request):
    if not request.user.is_authenticated:
        return redirect("login_view")

    context = get_base_context(request)

    conversations = DirectMessage.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).values(
        "sender", "receiver"
    ).distinct()

    conversation_users = set()
    for conv in conversations:
        if conv["sender"] != request.user.id:
            conversation_users.add(conv["sender"])
        if conv["receiver"] != request.user.id:
            conversation_users.add(conv["receiver"])

    users_with_messages = User.objects.filter(id__in=conversation_users)

    conversations_data = []
    for user in users_with_messages:
        last_message = DirectMessage.objects.filter(
            Q(sender=request.user, receiver=user) |
            Q(sender=user, receiver=request.user)
        ).order_by("-created_at").first()

        unread_count = DirectMessage.objects.filter(
            sender=user,
            receiver=request.user,
            is_read=False
        ).count()

        conversations_data.append({
            "user": user,
            "last_message": last_message,
            "unread_count": unread_count,
        })

    conversations_data.sort(key=lambda x: x["last_message"].created_at if x["last_message"] else timezone.now(), reverse=True)

    context.update({
        "title": "Повідомлення",
        "conversations": conversations_data,
    })

    return render(request, "myapp/messages_list.html", context)


def conversation_view(request, username):
    if not request.user.is_authenticated:
        return redirect("login_view")

    context = get_base_context(request)

    other_user = get_object_or_404(User, username=username)

    are_friends = Friendship.objects.filter(
        Q(from_user=request.user, to_user=other_user, status="accepted") |
        Q(from_user=other_user, to_user=request.user, status="accepted")
    ).exists()

    if not are_friends:
        return redirect("friends_list")

    messages = DirectMessage.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).select_related("sender", "receiver").order_by("created_at")

    DirectMessage.objects.filter(
        sender=other_user,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        media_file = request.FILES.get("media_file")

        if text or media_file:
            DirectMessage.objects.create(
                sender=request.user,
                receiver=other_user,
                text=text,
                media_file=media_file
            )

            return redirect("conversation", username=username)

    sender_profile = UserProfile.objects.filter(user=request.user).first()
    receiver_profile = UserProfile.objects.filter(user=other_user).first()

    message_items = []
    for msg in messages:
        avatar_url = ""
        if msg.sender == request.user and sender_profile and sender_profile.avatar_file:
            avatar_url = sender_profile.avatar_file.url
        elif msg.sender == other_user and receiver_profile and receiver_profile.avatar_file:
            avatar_url = receiver_profile.avatar_file.url

        media_url = ""
        media_is_video = False
        if msg.media_file:
            media_url = msg.media_file.url
            media_is_video = is_video_file(media_url)

        message_items.append({
            "message": msg,
            "avatar_url": avatar_url,
            "media_url": media_url,
            "media_is_video": media_is_video,
        })

    context.update({
        "title": f"Діалог з {other_user.username}",
        "other_user": other_user,
        "messages": messages,
        "message_items": message_items,
    })

    return render(request, "myapp/conversation.html", context)


def notifications_view(request):
    if not request.user.is_authenticated:
        return redirect("login_view")

    context = get_base_context(request)

    notifications = Notification.objects.filter(
        user=request.user
    ).select_related("from_user", "comment", "comment__post").order_by("-created_at")

    # Позначити всі як прочитані
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    context.update({
        "title": "Сповіщення",
        "notifications": notifications,
    })

    return render(request, "myapp/notifications.html", context)


def search_users_view(request):
    if not request.user.is_authenticated:
        return redirect("login_view")

    context = get_base_context(request)

    search_query = request.GET.get("q", "").strip()
    search_results = []

    if search_query:
        search_results = User.objects.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
        ).exclude(id=request.user.id)[:20]

        # Додати інформацію про статус дружби
        for user in search_results:
            friendship = Friendship.objects.filter(
                Q(from_user=request.user, to_user=user) |
                Q(from_user=user, to_user=request.user)
            ).first()

            if friendship:
                if friendship.status == "accepted":
                    user.friendship_status = "accepted"
                elif friendship.from_user == request.user:
                    user.friendship_status = "pending_sent"
                else:
                    user.friendship_status = "pending_received"
            else:
                user.friendship_status = None

    context.update({
        "title": "Пошук користувачів",
        "search_query": search_query,
        "search_results": search_results,
    })

    return render(request, "myapp/search_users.html", context)
