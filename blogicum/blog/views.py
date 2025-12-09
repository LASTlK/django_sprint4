from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from blog.models import Post, Category, Comment
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from .forms import PostForm
from django.contrib import messages
from django.shortcuts import redirect
from .forms import CommentForm
from django.utils import timezone


User = get_user_model()


def index(request):
    post_list = Post.objects.filter(
        Q(pub_date__lte=timezone.now())
        & Q(is_published=True)
        & Q(category__is_published=True)
    ).select_related('category', 'location').annotate(
        comment_count=Count('comments')).order_by('-pub_date')

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def post_detail(request, id):
    post = get_object_or_404(Post.objects.select_related(
        'author', 'category', 'location'), pk=id)

    is_author = request.user.is_authenticated and request.user == post.author
    is_published = post.is_published and (
        post.pub_date <= timezone.now() and post.category.is_published)

    if not is_published and not is_author:
        return render(request, 'pages/404.html', status=404)

    comments = post.comments.all().select_related('author')
    form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    post_list = Post.objects.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category=category
    ).select_related('category', 'location').annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj, 'category': category}
    return render(request, 'blog/category.html', context)


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user

            if not post.pub_date:
                post.pub_date = timezone.now()

            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()

    context = {'form': form}
    return render(request, 'blog/create.html', context)


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    if request.user == profile_user:
        posts = Post.objects.filter(author=profile_user)
    else:
        posts = Post.objects.filter(
            author=profile_user,
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )

    posts = posts.select_related('author', 'category', 'location').annotate(
        comment_count=Count('comments')).order_by('-pub_date')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile': profile_user,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ['first_name', 'last_name', 'email']
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        return self.request.user


@login_required
def edit_post(request, id):
    post = get_object_or_404(Post, pk=id)

    if post.author != request.user:
        return redirect('blog:post_detail', id=id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=id)
    else:
        form = PostForm(instance=post)

    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
    return redirect('blog:post_detail', id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, author=request.user)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=post_id)
    else:
        form = CommentForm(instance=comment)

    context = {
        'form': form,
        'comment': comment,
    }
    return render(request, 'blog/comment.html', context)


@login_required
def delete_post(request, id):
    post = get_object_or_404(Post, pk=id, author=request.user)

    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)

    form = PostForm(instance=post)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, author=request.user)

    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Комментарий удален!')
        return redirect('blog:post_detail', id=post_id)

    context = {'comment': comment}
    return render(request, 'blog/comment.html', context)
