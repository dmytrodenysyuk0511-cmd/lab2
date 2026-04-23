from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("create/", views.create_post, name="create_post"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),

    path("store/", views.store_home, name="store_home"),
    path("store/category/<int:category_id>/", views.product_category_detail, name="product_category_detail"),
    path("store/product/<int:product_id>/", views.product_detail, name="product_detail"),
    path("store/product/<int:product_id>/rate/", views.rate_product, name="rate_product"),
    path("store/buy/<int:product_id>/", views.buy_product, name="buy_product"),

    path("cart/", views.cart_view, name="cart_view"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/checkout/", views.checkout_cart, name="checkout_cart"),

    path("newsletter/subscribe/", views.newsletter_subscribe, name="newsletter_subscribe"),

    path("category/<int:category_id>/", views.category_posts, name="category_posts"),
    path("post/<int:post_id>/", views.post_detail, name="post_detail"),
]