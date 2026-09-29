from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from posts.models import Post

from .models import Follow


def register(request):
    if request.user.is_authenticated:
        return redirect("feed")

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("login")

    else:
        form = UserCreationForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form}
    )
  


@login_required
def profile(request, username=None):
    if username:
        profile_user = get_object_or_404(
            User,
            username=username
        )
    else:
        profile_user = request.user

    posts = Post.objects.filter(
        user=profile_user
    ).order_by("-created_at")

    followers_count = Follow.objects.filter(
        following=profile_user
    ).count()

    following_count = Follow.objects.filter(
        follower=profile_user
    ).count()

    is_own_profile = (
        request.user == profile_user
    )

    is_following = False

    if not is_own_profile:
        is_following = Follow.objects.filter(
            follower=request.user,
            following=profile_user
        ).exists()

    return render(
        request,
        "accounts/profile.html",
        {
            "profile_user": profile_user,
            "posts": posts,
            "followers_count": followers_count,
            "following_count": following_count,
            "is_own_profile": is_own_profile,
            "is_following": is_following,
        }
    )


@login_required
@require_POST
def toggle_follow(request, username):
    user_to_follow = get_object_or_404(
        User,
        username=username
    )

    if user_to_follow == request.user:
        return redirect(
            "user_profile",
            username=username
        )

    follow = Follow.objects.filter(
        follower=request.user,
        following=user_to_follow
    ).first()

    if follow:
        follow.delete()

    else:
        Follow.objects.create(
            follower=request.user,
            following=user_to_follow
        )

    return redirect(
        "user_profile",
        username=username
    )