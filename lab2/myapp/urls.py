from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("create/", views.create_post, name="create_post"),

    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login_view"),
    path("logout/", views.logout_view, name="logout"),

    path("password-reset/", views.password_reset_request_view, name="password_reset_request_view"),
    path("password-reset/confirm/", views.password_reset_confirm_view, name="password_reset_confirm_view"),

    path("profile/", views.profile_view, name="profile"),
    path("settings/", views.account_settings_view, name="account_settings"),
    path("saved/", views.saved_items_view, name="saved_items"),
    path("user/<str:username>/", views.public_profile_view, name="public_profile"),

    path("save/post/<int:post_id>/", views.toggle_save_post, name="toggle_save_post"),
    path("save/comment/<int:comment_id>/", views.toggle_save_comment, name="toggle_save_comment"),

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

    path("friends/", views.friends_list_view, name="friends_list"),
    path("friends/add/<str:username>/", views.send_friend_request, name="send_friend_request"),
    path("friends/accept/<int:request_id>/", views.accept_friend_request, name="accept_friend_request"),
    path("friends/reject/<int:request_id>/", views.reject_friend_request, name="reject_friend_request"),
    path("friends/remove/<str:username>/", views.remove_friend, name="remove_friend"),
    path("friends/search/", views.search_users_view, name="search_users"),

    path("messages/", views.messages_list_view, name="messages_list"),
    path("messages/<str:username>/", views.conversation_view, name="conversation"),

    path("notifications/", views.notifications_view, name="notifications"),
]