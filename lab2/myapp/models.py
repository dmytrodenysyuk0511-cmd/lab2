from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва")
    description = models.TextField(blank=True, default="", verbose_name="Опис")
    avatar_file = models.FileField(
        upload_to="forum/category_avatars/",
        blank=True,
        null=True,
        verbose_name="Аватарка основної теми"
    )
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
        verbose_name="Основна тема"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="forum_topics",
        verbose_name="Користувач"
    )
    author_name = models.CharField(max_length=100, default="Користувач", verbose_name="Автор")
    title = models.CharField(max_length=200, verbose_name="Назва підтеми")
    content = models.TextField(verbose_name="Опис підтеми")
    avatar_file = models.FileField(
        upload_to="forum/topic_avatars/",
        blank=True,
        null=True,
        verbose_name="Аватарка підтеми"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    def __str__(self):
        return self.title

    def replies_count(self):
        return self.comments.count()

    class Meta:
        verbose_name = "Підтема"
        verbose_name_plural = "Підтеми"


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Підтема"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="forum_messages",
        verbose_name="Користувач"
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="answers",
        verbose_name="Відповідь на повідомлення"
    )
    author_name = models.CharField(max_length=100, verbose_name="Автор")
    text = models.TextField(blank=True, default="", verbose_name="Повідомлення")
    media_file = models.FileField(
        upload_to="forum/chat_media/",
        blank=True,
        null=True,
        verbose_name="Фото або відео"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    def __str__(self):
        return f"{self.author_name} - {self.post.title}"

    class Meta:
        verbose_name = "Повідомлення"
        verbose_name_plural = "Повідомлення"


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

    avatar_url = models.URLField(blank=True, default="", verbose_name="Фото профілю старе")
    live_photo_url = models.URLField(blank=True, default="", verbose_name="Live photo старе")

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
        verbose_name="Live background"
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


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Кількість")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

    class Meta:
        verbose_name = "Кошик"
        verbose_name_plural = "Кошик"
        unique_together = ("user", "product")


class NewsletterSubscriber(models.Model):
    name = models.CharField(max_length=100, verbose_name="Ім'я")
    email = models.EmailField(unique=True, verbose_name="Email")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Підписник розсилки"
        verbose_name_plural = "Підписники розсилки"


class ProductRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="product_ratings")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="ratings")
    score = models.PositiveSmallIntegerField(
        verbose_name="Оцінка",
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, default="", verbose_name="Коментар")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    def __str__(self):
        return f"{self.product.name} - {self.score}"

    class Meta:
        verbose_name = "Оцінка товару"
        verbose_name_plural = "Оцінки товарів"
        unique_together = ("user", "product")


class Order(models.Model):
    STATUS_CHOICES = [
        ("new", "Нове"),
        ("completed", "Завершене"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders", verbose_name="Користувач")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Загальна сума")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new", verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Замовлення")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    product_name = models.CharField(max_length=150, verbose_name="Назва товару")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Кількість")

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    class Meta:
        verbose_name = "Позиція замовлення"
        verbose_name_plural = "Позиції замовлення"


class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reset_codes")
    email = models.EmailField(verbose_name="Email")
    code = models.CharField(max_length=6, verbose_name="Код")
    is_used = models.BooleanField(default=False, verbose_name="Використано")
    expires_at = models.DateTimeField(verbose_name="Дійсний до")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")

    def is_valid(self):
        return not self.is_used and timezone.now() <= self.expires_at

    def __str__(self):
        return f"{self.email} - {self.code}"

    class Meta:
        verbose_name = "Код відновлення пароля"
        verbose_name_plural = "Коди відновлення пароля"


class SavedItem(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="saved_items",
        verbose_name="Користувач"
    )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="saved_items",
        null=True,
        blank=True,
        verbose_name="Збережена підтема"
    )

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="saved_items",
        null=True,
        blank=True,
        verbose_name="Збережене повідомлення"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Збережено")

    def __str__(self):
        if self.post:
            return f"{self.user.username} зберіг тему: {self.post.title}"

        if self.comment:
            return f"{self.user.username} зберіг повідомлення"

        return f"{self.user.username} збережене"

    class Meta:
        verbose_name = "Збережене"
        verbose_name_plural = "Збережене"
        unique_together = (
            ("user", "post"),
            ("user", "comment"),
        )


class Friendship(models.Model):
    STATUS_CHOICES = [
        ("pending", "Очікує"),
        ("accepted", "Прийнято"),
        ("rejected", "Відхилено"),
    ]

    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_friend_requests",
        verbose_name="Від користувача"
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_friend_requests",
        verbose_name="До користувача"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="Статус"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username} ({self.status})"

    class Meta:
        verbose_name = "Дружба"
        verbose_name_plural = "Дружба"
        unique_together = ("from_user", "to_user")


class DirectMessage(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_direct_messages",
        verbose_name="Відправник"
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_direct_messages",
        verbose_name="Отримувач"
    )
    text = models.TextField(verbose_name="Повідомлення")
    media_file = models.FileField(
        upload_to="direct_messages/",
        blank=True,
        null=True,
        verbose_name="Фото або відео"
    )
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}: {self.text[:30]}"

    class Meta:
        verbose_name = "Приватне повідомлення"
        verbose_name_plural = "Приватні повідомлення"
        ordering = ["created_at"]


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("reply", "Відповідь на повідомлення"),
        ("mention", "Згадування"),
        ("friend_request", "Запит на дружбу"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Користувач"
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default="reply",
        verbose_name="Тип сповіщення"
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
        verbose_name="Повідомлення"
    )
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_notifications",
        null=True,
        blank=True,
        verbose_name="Від користувача"
    )
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")

    def __str__(self):
        return f"{self.user.username} - {self.notification_type}"

    class Meta:
        verbose_name = "Сповіщення"
        verbose_name_plural = "Сповіщення"
        ordering = ["-created_at"]