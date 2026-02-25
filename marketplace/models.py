from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    product_name = models.CharField(max_length=255)
    price = models.CharField(max_length=255)
    product_description = models.TextField()
    product_image = models.ImageField(upload_to='products/', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')  # Track the creator
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set the time when the post is created


    def __str__(self):
        return self.product_name

