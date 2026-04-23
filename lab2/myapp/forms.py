from django import forms
from .models import Post, Comment, UserProfile


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
            "song_file": forms.ClearableFileInput(attrs={"accept": "audio/*"}),
        }