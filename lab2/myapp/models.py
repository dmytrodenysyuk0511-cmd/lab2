from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва")
    description = models.TextField(blank=True, default="", verbose_name="Опис")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категорія форуму"
        verbose_name_plural = "Категорії форуму"


class Post(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Категорія"
    )
    author_name = models.CharField(max_length=100, default="Користувач", verbose_name="Автор")
    title = models.CharField(max_length=200, verbose_name="Назва")
    content = models.TextField(verbose_name="Текст теми")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Теми"


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Тема"
    )
    author_name = models.CharField(max_length=100, verbose_name="Автор")
    text = models.TextField(verbose_name="Текст відповіді")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    def __str__(self):
        return f"{self.author_name} - {self.post.title}"

    class Meta:
        verbose_name = "Відповідь"
        verbose_name_plural = "Відповіді"


class ProductCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва")
    description = models.TextField(blank=True, default="", verbose_name="Опис")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категорія товарів"
        verbose_name_plural = "Категорії товарів"


class Product(models.Model):
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Категорія"
    )
    name = models.CharField(max_length=150, verbose_name="Назва")
    short_description = models.CharField(max_length=255, verbose_name="Короткий опис")
    description = models.TextField(verbose_name="Опис")
    image_url = models.URLField(blank=True, default="", verbose_name="Посилання на фото")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Ціна")
    unlocks_plus = models.BooleanField(default=False, verbose_name="Відкриває UNIChat Plus")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товари"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="forum_profile")
    is_plus = models.BooleanField(default=False, verbose_name="UNIChat Plus")
    plus_plan = models.CharField(max_length=150, blank=True, default="", verbose_name="Тариф")

    avatar_url = models.URLField(blank=True, default="", verbose_name="Фото профілю (старе поле)")
    live_photo_url = models.URLField(blank=True, default="", verbose_name="Live photo (старе поле)")

    avatar_file = models.FileField(
        upload_to="profile/avatars/",
        blank=True,
        null=True,
        verbose_name="Файл фото профілю"
    )
    live_photo_file = models.FileField(
        upload_to="profile/live_photos/",
        blank=True,
        null=True,
        verbose_name="Файл live photo"
    )
    song_file = models.FileField(
        upload_to="profile/songs/",
        blank=True,
        null=True,
        verbose_name="Файл пісні"
    )

    favorite_song = models.CharField(max_length=255, blank=True, default="", verbose_name="Назва пісні")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Профіль користувача"
        verbose_name_plural = "Профілі користувачів"