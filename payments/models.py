from django.db import models
from django.contrib.auth.models import User
from marketplace.models import Product  # Assuming you have a Product model

class Seller_Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Linking to the Django User model
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.user.username  


class Transaction(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Success", "Success"),
        ("Failed", "Failed"),
        ("Cancelled", "Cancelled"),
    ]

    seller = models.ForeignKey(Seller_Account, on_delete=models.CASCADE, related_name="transactions")
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    transaction_date = models.DateTimeField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product")

    def __str__(self):
        return f"Transaction {self.mpesa_receipt_number or self.transaction_id} - {self.status}"

    def update_balance(self):
        if self.status == "Success":
            self.seller.balance += self.amount
            self.seller.save()
            print("Account updated successfully")
