from django.urls import path

from . import views

urlpatterns = [

    path('marketplace/', views.marketplace, name='marketplace'),
    path('create_product/', views.create_product, name='create_product'),
    path('post_product/', views.post_product, name='post_product'),
    path('products/<int:product_id>/update', views.update_product, name='update_product'),
    path('products/<int:product_id>/delete', views.delete_product, name='delete_product'),
    path('myproducts/', views.myproducts, name='myproducts'),

]