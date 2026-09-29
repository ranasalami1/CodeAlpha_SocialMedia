from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CommentForm, PostForm
from .models import Like, Post


@login_required
def feed(request):
    posts = Post.objects.all().order_by("-created_at")

    for post in posts:
        post.liked_by_user = post.likes.filter(
            user=request.user
        ).exists()

        post.like_count = post.likes.count()

    comment_form = CommentForm()

    return render(
        request,
        "posts/feed.html",
        {
            "posts": posts,
            "comment_form": comment_form,
        },
    )


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()

            return redirect("feed")

    else:
        form = PostForm()

    return render(
        request,
        "posts/create_post.html",
        {"form": form},
    )


@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
    )

    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)

        comment.post = post
        comment.user = request.user

        comment.save()

    return redirect("feed")


@login_required
@require_POST
def toggle_like(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
    )

    like = Like.objects.filter(
        post=post,
        user=request.user,
    ).first()

    if like:
        like.delete()

    else:
        Like.objects.create(
            post=post,
            user=request.user,
        )

    return redirect("feed")