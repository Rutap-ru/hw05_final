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
    author_profile = get_object_or_404(User, username=username)
    post_list = author_profile.author_post.all()

    follow_user = (request.user.is_authenticated
                   and author_profile != request.user
                   and author_profile.following.filter(user=request.user))

    subscriptions = author_profile.follower.count()
    subscribers = author_profile.following.count()

    paginator = Paginator(post_list, POSTS_PER_PAGE)

    page_number = request.GET.get('page')

    page = paginator.get_page(page_number)
    return render(
        request,
        'profile.html',
        {
            'author_profile': author_profile,
            'page': page,
            'paginator': paginator,
            'following': follow_user,
            'subscriptions': subscriptions,
            'subscribers': subscribers,
        }
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    author_posts_count = post.author.author_post.count()

    follow_user = (request.user.is_authenticated
                   and post.author != request.user
                   and post.author.following.filter(user=request.user))

    subscriptions = post.author.follower.count()
    subscribers = post.author.following.count()

    form = CommentForm()
    comments = post.comments.all()
    return render(
        request, 'post.html',
        {
            'author_profile': post.author,
            'author_posts_count': author_posts_count,
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
        'follow.html',
        {'page': page, 'paginator': paginator}
    )


@login_required
def profile_follow(request, username):
    author_profile = get_object_or_404(User, username=username)
    if author_profile != request.user:
        Follow.objects.get_or_create(user=request.user, author=author_profile)
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    subscription = get_object_or_404(
        Follow,
        user=request.user,
        author__username=username
    )
    subscription.delete()
    return redirect('profile', username)


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)
