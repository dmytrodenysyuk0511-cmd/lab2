from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Comment, UserProfile, NewsletterSubscriber, ProductRating


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["category", "title", "content", "avatar_file"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Назва підтеми"}),
            "content": forms.Textarea(attrs={"placeholder": "Опиши, про що буде ця підтема", "rows": 5}),
            "avatar_file": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text", "media_file"]
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "placeholder": "Напиши повідомлення...",
                    "rows": 3,
                    "class": "chat-textarea",
                }
            ),
            "media_file": forms.ClearableFileInput(
                attrs={
                    "accept": "image/*,video/mp4,video/webm,video/quicktime",
                    "class": "chat-media-input",
                }
            ),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["avatar_file", "live_photo_file", "song_file", "favorite_song"]
        widgets = {
            "avatar_file": forms.ClearableFileInput(attrs={"accept": "image/*"}),
            "live_photo_file": forms.ClearableFileInput(attrs={"accept": "image/*,video/mp4,video/webm,video/quicktime"}),
            "song_file": forms.ClearableFileInput(attrs={"accept": "audio/*"}),
            "favorite_song": forms.TextInput(attrs={"placeholder": "Назва пісні або треку"}),
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
            "comment": forms.Textarea(attrs={"rows": 4}),
        }


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Користувач з таким email уже існує.")

        return email


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Логін")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Email")


class PasswordResetConfirmForm(forms.Form):
    email = forms.EmailField(label="Email")
    code = forms.CharField(max_length=6, label="Тимчасовий код")
    new_password1 = forms.CharField(label="Новий пароль", widget=forms.PasswordInput)
    new_password2 = forms.CharField(label="Повтори пароль", widget=forms.PasswordInput)