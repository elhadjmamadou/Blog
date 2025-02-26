from django.urls import path
from .views import BlogHom,BlogPostCreate,BlogPostUpdate,BlogPostDetail,BlogPostDelete
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from .views import SignUpView, home,CommentUpdateView, CommentDeleteView,profile_update, contact

app_name = "posts"

urlpatterns = [
    path('', home, name='acceuil'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path("blog/",BlogHom.as_view(), name="home" ),
    path("create/",BlogPostCreate.as_view(), name="create"),
    path('contact/', contact, name='contact'),  
    path("<str:slug>/",login_required(BlogPostDetail.as_view()), name="post"),
    path("edit/<str:slug>/",BlogPostUpdate.as_view(), name="edit"),
    path("delete/<str:slug>/",BlogPostDelete.as_view(), name="delete"),
    path('comment/edit/<int:pk>/', CommentUpdateView.as_view(), name='comment_edit'),
    path('comment/delete/<int:pk>/', CommentDeleteView.as_view(), name='comment_delete'),
    path('profile/update/', profile_update, name='profile_update'),
]
