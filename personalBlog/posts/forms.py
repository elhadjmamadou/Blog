from django import forms
from .models import Comment
from .models import BlogPost
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password1", "password2"]




class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'thumbnail', 'category', 'tags', 'published']
        widgets = {
            'tags': forms.CheckboxSelectMultiple,
        }


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

# Optionnel : Formulaire pour un modèle de profil utilisateur
# class ProfileUpdateForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         fields = ['bio', 'profile_picture']