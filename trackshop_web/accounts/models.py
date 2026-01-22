from django.db import models
from django.contrib.auth.models import User

class Shop(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="owned_shops")
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    default_currency = models.ForeignKey("trackshop.Currency", null=True, blank=True, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ("owner", "Propriétaire"),
        ("Manager", "Manager"),
        ("cashier", "Caissier"),
        ("viewer", "Lecture seule"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    active_shop = models.ForeignKey(Shop, null=True, blank=True, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "active_shop")

    def __str__(self):
        return f"{self.user.username} - {self.active_shop.name}"

