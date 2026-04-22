from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('category/<int:category_id>/', views.category_posts, name='category_posts'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
]