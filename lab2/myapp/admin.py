from django.contrib import admin
from .models import Category, Post, Comment, ProductCategory, Product, UserProfile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author_name", "category", "created_at", "updated_at")
    list_filter = ("category",)
    search_fields = ("title", "author_name", "content")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author_name", "post", "created_at", "updated_at")
    list_filter = ("post",)
    search_fields = ("author_name", "text")


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "unlocks_plus", "created_at", "updated_at")
    list_filter = ("category", "unlocks_plus")
    search_fields = ("name", "short_description", "description")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_plus", "plus_plan", "updated_at")
    search_fields = ("user__username", "plus_plan")