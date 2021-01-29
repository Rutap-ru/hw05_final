from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .constants import POSTS_PER_PAGE
from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)

    page_number = request.GET.get('page')

    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.group_post.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)

    page_number = request.GET.get('page')

    page = paginator.get_page(page_number)
    return render(
        request,
        'group.html',
        {'group': group, 'page': page, 'paginator': paginator}
    )


@login_required
def new_post(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        )

    if request.method == 'GET' or not form.is_valid():
        return render(request, 'new_post.html', {'form': form})

    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('index')


def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    post_list = user_profile.author_post.all()

    follow_user = False
    if request.user.is_authenticated:
        try:
            follow_user = user_profile.following.get(user=request.user)
        except Follow.DoesNotExist:
            follow_user = False

    subscriptions = user_profile.follower.count()
    subscribers = user_profile.following.count()

    paginator = Paginator(post_list, POSTS_PER_PAGE)

    page_number = request.GET.get('page')

    page = paginator.get_page(page_number)
    return render(
        request,
        'profile.html',
        {
            'user_profile': user_profile,
            'page': page,
            'paginator': paginator,
            'following': follow_user,
            'subscriptions': subscriptions,
            'subscribers': subscribers,
        }
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    user_post_count = post.author.author_post.all().count()

    follow_user = False
    if request.user.is_authenticated:
        try:
            follow_user = post.author.following.get(user=request.user)
        except Follow.DoesNotExist:
            follow_user = False

    subscriptions = post.author.follower.count()
    subscribers = post.author.following.count()

    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    return render(
        request, 'post.html',
        {
            'user_profile': post.author,
            'user_post_count': user_post_count,
            'post': post,
            'form': form,
            'comments': comments,
            'post_viewing': True,
            'following': follow_user,
            'subscriptions': subscriptions,
            'subscribers': subscribers,
        }
    )


def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('post', username, post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('post', username, post_id)

    return render(
        request,
        'new_post.html',
        {'form': form, 'post': post}
    )


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect('post', username, post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        "follow.html",
        {'page': page, 'paginator': paginator}
    )


@login_required
def profile_follow(request, username):
    user_profile = get_object_or_404(User, username=username)
    if user_profile != request.user:
        try:
            Follow.objects.create(user=request.user, author=user_profile)
        except:
            return redirect('profile', username)
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    try:
        Follow.objects.get(
            user=request.user,
            author__username=username
        ).delete()
        return redirect('profile', username)
    except:
        return redirect('profile', username)


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
