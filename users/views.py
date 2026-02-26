from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from django.db.models import Q

from users.models import Follow, Message, Profile
from posts.models import Post


def home_view(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == "POST":
        email_or_username = request.POST.get('username') 
        password = request.POST.get('password')

        
        try:
            user = User.objects.get(email=email_or_username)
            username = user.username  
        except User.DoesNotExist:
            username = email_or_username  

        # Authenticate using username
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')  
        else:
            messages.error(request, "Invalid email/username or password. Please try again.")
    
    return render(request, 'login.html')

def signup_view(request):
    return render(request, 'signup.html')

def register_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if the email or username already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists. Please use a different email or log in.")
            return render(request, 'signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose another username.")
            return render(request, 'signup.html')

        # Create and save the user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password  
        )
        user.save()

        messages.success(request, "Registration successful! Please log in.")
        return redirect('login')  

    return render(request, 'signup.html')

@login_required
def profile_view(request, username):
    # Get the user by username
    user = get_object_or_404(User, username=username)
    followers = user.followers.all()
    following = user.following.all()
    return render(request, 'profile.html', {
        'profile_user': user,
        'followers': followers,
        'following': following,
        'followers_count': followers.count(),
        'following_count': following.count(),
    })
    

@login_required
def update_profile_picture(request, username):
    if request.user.username != username:
        return redirect('profile_view', username=request.user.username)

    if request.method == 'POST':
        profile_picture = request.FILES.get('profile_picture')  
        if profile_picture:
            user_profile = get_object_or_404(Profile, user=request.user)
            user_profile.profile_picture = profile_picture
            user_profile.save()
            messages.success(request, "Profile picture updated successfully!")
        else:
            messages.error(request, "Please upload a valid image.")

    return redirect('profile_view', username=request.user.username)



@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        name = request.POST.get('name')
        email = request.POST.get('email')

        if name:
            user.first_name = name
        if email:
            user.email = email
        
        user.save()
        messages.success(request, "Profile updated successfully!")
    return redirect('profile_view', username=request.user.username)


@login_required
def view_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=profile_user)
    is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
    followers = profile_user.followers.all()
    following = profile_user.following.all()

    return render(request, 'view_profile.html', {        
        'profile_user': profile_user,
        'posts': posts,
        'is_following': is_following,
        'followers': followers,
        'following': following,
        'followers_count': followers.count(),
        'following_count': following.count(),
    })

    


@login_required
def user_list(request):
    query = request.GET.get('q', '')
    users = User.objects.all()

    if query:
        users = users.filter(Q(username__icontains=query))

    # Get the list of users the current user is following
    followed_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)

    context = {
        'users': users,
        'followed_users': followed_users,
        'query': query,
    }
    return render(request, 'user_list.html', context)



# View to handle following/unfollowing users
@login_required
def toggle_follow(request, username):
    user_to_follow = get_object_or_404(User, username=username)

    # Check if the current user is already following the other user
    existing_follow = Follow.objects.filter(follower=request.user, following=user_to_follow)
    if existing_follow.exists():
        # Unfollow the user if already followed
        existing_follow.delete()
    else:
        # Follow the user if not already followed
        Follow.objects.create(follower=request.user, following=user_to_follow)

    return redirect('user_list')



def toggleFollow(request, username):
    if request.method == 'POST':
        profile_user = get_object_or_404(User, username=username)
        if Follow.objects.filter(follower=request.user, following=profile_user).exists():
            Follow.objects.filter(follower=request.user, following=profile_user).delete()
            return JsonResponse({"message": "Unfollowed successfully!"})
        else:
            Follow.objects.create(follower=request.user, following=profile_user)
            return JsonResponse({"message": "Followed successfully!"})
    return JsonResponse({"message": "Invalid request method."}, status=400)
    

    
    
@login_required
def conversation_view(request, user_id):
    try:
        current_user = request.user
        other_user = get_object_or_404(User, id=user_id)
        users_with_messages = User.objects.exclude(id=request.user.id)

        # Retrieve messages between current user and the other user, ordered by timestamp
        messages = Message.objects.filter(
            (Q(sender=current_user) & Q(receiver=other_user)) |
            (Q(sender=other_user) & Q(receiver=current_user))
        ).order_by('timestamp') 

        context = {
            'messages': messages,
            'other_user': other_user,
            'users_with_messages': users_with_messages,
        }
        return render(request, 'conversation.html', context)

    except User.DoesNotExist:
        return render(request, 'error.html', {'message': 'User not found'})


@login_required
def messages_user_list(request):
    query = request.GET.get('q', '')
    users = User.objects.exclude(id=request.user.id)  
    if query:
        users = users.filter(username__icontains=query)

    context = {
        'users': users,
        'query': query,
    }
    return render(request, 'conversation.html', context)


@login_required
def send_message(request):
    if request.method == 'POST':
        content = request.POST.get('content', '')
        receiver_id = request.POST.get('receiver_id')
        current_user = request.user

        if content and receiver_id:
            receiver = get_object_or_404(User, id=receiver_id)

            # Create and save the message
            message = Message.objects.create(
                sender=current_user,
                receiver=receiver,
                content=content
            )
            # messages.success(request, "Message sent successfully!")

        return redirect('conversation_view', user_id=receiver_id)
    
@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "Logout successfull welcome back... ")
    return redirect('login')     

    
def custom_404_view(request, exception):
    return render(request, '404.html', status=404)    

