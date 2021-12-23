from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm
from .utils import get_page_obj


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    page_number = request.GET.get('page')
    page_obj = get_page_obj(post_list, page_number)
    text = 'Последние обновления на сайте'
    context = {
        'text': text,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    posts = group.posts.all()
    page_number = request.GET.get('page')
    page_obj = get_page_obj(posts, page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }

    return render(request, template, context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    user_posts = user.posts.all()
    user_posts_count = user_posts.count()
    page_number = request.GET.get('page')
    page_obj = get_page_obj(user_posts, page_number)
    context = {
        'author': user,
        'user_posts_count': user_posts_count,
        'page_obj': page_obj,
    }
    if request.user.is_authenticated:
        follow = Follow.objects.filter(user=request.user, author=user)
        if follow:
            following = True
        else:
            following = False
        context['following'] = following
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = post.author
    user_posts = user.posts.all()
    user_posts_count = user_posts.count()
    title = post.text[:30]
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post_id=post_id)
    context = {
        'post': post,
        'user_posts_count': user_posts_count,
        'title': title,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None)
    context = {'form': form}
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user.username)
    else:
        return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    is_edit = True
    post_to_edit = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post_to_edit)
    context = {'form': form,
               'post_to_edit': post_to_edit,
               'is_edit': is_edit}
    if not request.user.id == post_to_edit.author_id:
        return redirect('posts:post_detail', post_id=post_id)
    else:
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)
        else:
            return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, pk=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = []
    follows = Follow.objects.filter(user=request.user)
    for follow in follows:
        following_posts = Post.objects.filter(author=follow.author)
        for post in following_posts:
            posts.append(post)

    page_number = request.GET.get('page')
    page_obj = get_page_obj(posts, page_number)
    text = 'Посты авторов, на которых вы подписаны'
    context = {
        'text': text,
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    following = User.objects.filter(username=username)[0]
    if request.user != following:
        if not Follow.objects.filter(
            user=request.user,
            author=User.objects.filter(username=username)[0]
        ):
            Follow.objects.create(
                user=request.user,
                author=User.objects.filter(username=username)[0]
            )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user,
        author=User.objects.filter(username=username)[0]
    ).delete()
    return redirect('posts:profile', username=username)
