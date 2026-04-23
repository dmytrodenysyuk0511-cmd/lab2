from django import forms
from .models import Post, Comment, UserProfile, NewsletterSubscriber, ProductRating


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["category", "author_name", "title", "content"]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["author_name", "text"]


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["avatar_file", "live_photo_file", "song_file", "favorite_song"]
        widgets = {
            "favorite_song": forms.TextInput(attrs={"placeholder": "Введи назву пісні"}),
        }


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ["name", "email"]


class ProductRatingForm(forms.ModelForm):
    class Meta:
        model = ProductRating
        fields = ["score", "comment"]
        widgets = {
            "score": forms.Select(choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")]),
            "comment": forms.Textarea(attrs={"rows": 4, "placeholder": "Напиши короткий коментар"}),
        }