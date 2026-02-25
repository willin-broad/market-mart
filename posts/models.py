from django.db import models
from django.contrib.auth.models import User  # Import the User model

class Post(models.Model):
    description = models.TextField()
    image = models.ImageField(upload_to='posts/')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')  # ForeignKey to User
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set the time when the post is created

    def __str__(self):
        return f"Post by {self.user.username}"

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Liked by {self.user.username} post id {self.post.id}"

class Dislike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='dislikes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Disliked by {self.user.username} post id {self.post.id}"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commented by {self.user.username} post id {self.post.id}"