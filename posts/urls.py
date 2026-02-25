from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.view_posts, name='home'),
    path('create_post/', views.create_post, name='create_post'),
    path('post/', views.post, name='post'),
    path('posts/<int:post_id>/update/', views.update_post, name='update_post'),
    path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('dislike/<int:post_id>/', views.dislike_post, name='dislike_post'),
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('posts/<str:username>/', views.my_posts, name='my_posts'),
]