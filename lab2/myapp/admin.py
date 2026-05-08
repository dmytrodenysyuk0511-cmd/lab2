from django.contrib import admin
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
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at")
    search_fields = ("name", "description")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "author_name", "created_at", "updated_at")
    list_filter = ("category", "created_at")
    search_fields = ("title", "content", "author_name")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author_name", "created_at")
    list_filter = ("created_at",)
    search_fields = ("text", "author_name")


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at")
    search_fields = ("name", "description")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "unlocks_plus", "created_at")
    list_filter = ("category", "unlocks_plus")
    search_fields = ("name", "short_description", "description")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_plus", "plus_plan", "updated_at")
    list_filter = ("is_plus",)
    search_fields = ("user__username", "user__email", "plus_plan")


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "quantity", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "product__name")


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email")


@admin.register(ProductRating)
class ProductRatingAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "score", "created_at")
    list_filter = ("score", "created_at")
    search_fields = ("user__username", "product__name", "comment")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_price", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email")
    inlines = [OrderItemInline]


@admin.register(PasswordResetCode)
class PasswordResetCodeAdmin(admin.ModelAdmin):
    list_display = ("email", "code", "is_used", "expires_at", "created_at")
    list_filter = ("is_used", "created_at")
    search_fields = ("email", "code")


@admin.register(SavedItem)
class SavedItemAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "comment", "created_at")
    list_filter = ("created_at",)
    search_fields = (
        "user__username",
        "post__title",
        "comment__text",
    )