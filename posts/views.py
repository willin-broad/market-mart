from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from posts.models import Post, Like, Dislike, Comment
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User

@login_required
def create_post(request):
    return render(request, 'create_post.html')

@login_required
def post(request):
    if request.method == "POST":
        description = request.POST['description']
        image = request.FILES.get('image')

        # Create a new post and associate it with the current logged-in user
        post = Post(
            description=description,
            image=image,
            user=request.user 
        )
        post.save()

        return redirect('home')  

    return render(request, 'create_post.html')

@login_required
def view_posts(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'posts.html', {"posts": posts})

@login_required
def my_posts(request, username):
    # Get the user by username
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=user).order_by('-created_at')
    return render(request, 'mypost.html', {'posts': posts, 'user': user})


@login_required
def update_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Check if the logged-in user is the owner of the product
    if post.user != request.user:
        return HttpResponseForbidden("You are not allowed to update this product.")

    if request.method == "POST":
        post.description = request.POST['description']
        if 'image' in request.FILES:
            post.image = request.FILES['image']
        post.save()
        return redirect('home')

    return render(request, 'update_post.html', {'post': post})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Check if the logged-in user is the owner of the product
    if post.user != request.user:
        return HttpResponseForbidden("You are not allowed to delete this product.")

    if request.method == "POST":
        post.delete()
        return redirect('home')

    return render(request, 'delete_post.html', {'post': post})


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    existing_dislike = Dislike.objects.filter(post=post, user=request.user).first()

    if existing_dislike:
        existing_dislike.delete()  # Remove dislike if it exists

    like, created = Like.objects.get_or_create(post=post, user=request.user)

    if not created:
        like.delete()  

    return JsonResponse({"likes_count": post.likes.count()})

@login_required
def dislike_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    existing_like = Like.objects.filter(post=post, user=request.user).first()

    if existing_like:
        existing_like.delete()  #

    dislike, created = Dislike.objects.get_or_create(post=post, user=request.user)

    if not created:
        dislike.delete()  
        
    return JsonResponse({"dislikes_count": post.dislikes.count()})

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        text = request.POST.get('text')
        Comment.objects.create(post=post, user=request.user, text=text)

    return JsonResponse({
        "comments_count": post.comments.count(),
        "comments": [
            {"user": comment.user.username, "text": comment.text}
            for comment in post.comments.all()
        ]
    })

