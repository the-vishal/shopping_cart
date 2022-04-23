from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


# Create your models here.

@receiver(models.signals.post_save, sender=User)
def user_created(sender, instance, created, **kwargs):
    if created:
        Token.objects.create(user=user)


class Product(models.Model):
	id =  models.PositiveIntegerField(unique=True, primary_key=True)
	name = models.CharField(null=True, blank=True, max_length=20)
	price = models.FloatField(default=0.0)
	description = models.CharField(null=True, blank=True, max_length=500)
	category = models.CharField(null=True, blank=True, max_length=200)
	image = models.CharField(null=True, blank=True, max_length=500)
	discount_percentage = models.FloatField(default=None)
	weight_in_grams = models.FloatField(default=0.0)

class CartItem(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	quantity = models.PositiveIntegerField(default=0)

class Cart(models.Model):
	user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
	items = models.ManyToManyField(CartItem)

	def get_checkout_value():
		pass
