from django.shortcuts import (
    render,
    get_object_or_404,
    redirect,
    reverse,
    HttpResponseRedirect
)
from django.contrib.auth.decorators import login_required

from .models import Post, Group, User
from .forms import PostForm, CommentForm
from .utils import numbers_of_page


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.all()
    page_obj = numbers_of_page(request, posts)
    return render(request, template, {'page_obj': page_obj})


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = numbers_of_page(request, posts)
    return render(request, template, {
        'group': group,
        'page_obj': page_obj
    })


def profile(request, username):
    template = 'posts/profile.html'
    user = get_object_or_404(User, username=username)
    posts = user.posts.select_related('author')
    page_obj = numbers_of_page(request, posts)
    context = {
        'username': user,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm
    comments = post.comments.select_related('author').all()
    return render(request, template, {
        'post': post,
        'comments': comments,
        'form': form,
    })


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if not form.is_valid():
        form = PostForm()
        return render(request, 'posts/create_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return HttpResponseRedirect(reverse(
        'posts:profile',
        args=(post.author, )
    ))


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:post_detail', post_id)
    form = PostForm(instance=post)
    return render(request, 'posts/create_post.html', {
        'form': form,
        'is_edit': True
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)
