from django.urls import path
from django.conf.urls import handler404
from django.contrib.auth import views as auth_views

from . import views


handler404 = views.custom_404_view

urlpatterns = [
    path('', views.home_view, name='home_logout'), 
    path('accounts/login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('register/', views.register_view, name='register'),
    path('profile/<str:username>/update_picture/', views.update_profile_picture, name='update_profile_picture'),
    path('profile/<str:username>/', views.profile_view, name='profile_view'),
    path('update/', views.update_profile, name='update_profile'),
    path('user/<str:username>/', views.view_profile, name='view_profile'),
    path('profile/<str:username>/toggle-follow/', views.toggle_follow, name='toggle_follow'),
    path('profile/<str:username>/toggle-follow/', views.toggleFollow, name='togglefollow'),
    path('messages/conversation/<int:user_id>/', views.conversation_view, name='conversation_view'),
    path('messages/send/', views.send_message, name='send_message'),
    path('users/', views.user_list, name='user_list'),
    path('users_messages/', views.messages_user_list, name='user_list_messages'),   
    path('logout/', views.user_logout, name='logout'), 


     path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), 
         name='password_reset_complete'),
    
]