from django.shortcuts import render,redirect
from django.views.generic import ListView,  CreateView, UpdateView, DetailView,DeleteView
from .models import BlogPost, Comment
from django.urls import reverse_lazy
# from django.contrib.auth.forms import UserCreationForm
from .forms import CommentForm,UserUpdateForm,CustomUserCreationForm, ContactForm
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .models import Category, Tag
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages




def home(request):
    context = {}
    if not request.user.is_authenticated:
        context['show_login_signup'] = True
    return render(request, 'posts/home.html', context)


# class SignUpView(CreateView):
#     form_class = UserCreationForm
#     template_name = 'registration/signup.html'
#     success_url = reverse_lazy('posts:login')

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('posts:login')

class BlogHom(ListView):
    model = BlogPost
    context_object_name = "posts"
    template_name = "posts/blogpost_list.html"  # Assurez-vous que ce template existe

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtrer par statut de publication si l'utilisateur n'est pas authentifié
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(published=True)

        # Filtrer par catégorie
        category_slug = self.request.GET.get('category')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)

        # Filtrer par tag
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            tag = get_object_or_404(Tag, slug=tag_slug)
            queryset = queryset.filter(tags=tag)

        # Recherche par mot-clé
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(content__icontains=search_query)
            )

        return queryset


class BlogPostCreate(CreateView):
    model = BlogPost
    template_name = "posts/blogpost_create.html"
    fields = ["title", "content","thumbnail"]
    def form_valid(self, form):
        # Associer l'auteur connecté à l'article
        form.instance.author = self.request.user
        return super().form_valid(form)


class BlogPostUpdate(UpdateView, UserPassesTestMixin, LoginRequiredMixin):
    model = BlogPost
    template_name = "posts/blogpost_edit.html"
    fields = ["title", "content", "published"]
    success_url = reverse_lazy("posts:home")
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author



class BlogPostDetail(DetailView):
    model = BlogPost
    template_name = "posts/blogpost_detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['form'] = CommentForm()
        context['comments'] = self.object.comments.all()
        return context

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
        return self.get(request, *args, **kwargs)


class BlogPostDelete(DeleteView, UserPassesTestMixin, LoginRequiredMixin):
    model = BlogPost
    success_url = reverse_lazy("posts:home")
    template_name = "posts/blogpost_confirm_delete.html"
    context_object_name = "post"
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author



class CommentUpdateView(UpdateView):
    model = Comment
    template_name = 'posts/comment_form.html'
    fields = ['content']

    def get_success_url(self):
        comment = self.get_object()
        post = comment.post  # Assurez-vous que vous avez une relation entre Comment et Post
        return reverse('posts:post', kwargs={'slug': post.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comment = self.get_object()
        context['post'] = comment.post  # Assurez-vous que `comment.post` est correct
        return context


class CommentDeleteView(DeleteView):
    model = Comment
    template_name = 'posts/comment_confirm_delete.html'

    def get_success_url(self):
        comment = self.get_object()
        post = comment.post  # Assurez-vous que le champ `post` pointe correctement vers le modèle `BlogPost`
        return reverse('posts:post', kwargs={'slug': post.slug})


@login_required
def profile_update(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        # profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.userprofile)  # Optionnel

        if user_form.is_valid():  # and profile_form.is_valid():  # Optionnel
            user_form.save()
            # profile_form.save()  # Optionnel
            return redirect('posts:home')  # Redirige vers une page de confirmation ou le profil utilisateur

    else:
        user_form = UserUpdateForm(instance=request.user)
        # profile_form = ProfileUpdateForm(instance=request.user.userprofile)  # Optionnel

    context = {
        'user_form': user_form,
        # 'profile_form': profile_form  # Optionnel
    }

    return render(request, 'posts/profile_update.html', context)


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            
            # Envoyer l'email de notification
            subject = f'Nouveau message de contact: {contact_message.subject}'
            message = f"""
            Nouveau message reçu de {contact_message.name} ({contact_message.email})
            
            Sujet: {contact_message.subject}
            
            Message:
            {contact_message.message}
            """
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL],
                    fail_silently=False,
                )
                messages.success(request, "Votre message a été envoyé avec succès!")
            except Exception as e:
                messages.error(request, "Une erreur s'est produite lors de l'envoi du message.")
                
            return redirect('contact')
    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form': form})