from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response

import requests
from django.conf import settings
from cart.models import Product, CartItem


class AddItemView(APIView):

	def post(self, request):
		data = request.data
		pid = data.get('product_id')
		qty = data.get('quantity')
		user = request.user
		cart, exists = Cart.objects.get_or_create(user=user)
		
		product = self.fetch_product_info(pid)
		citem = CartItem.objects.create(product=product, quantity=qty)
		cart.items.add(citem)

		return Response([
		  {
		    "status": "success",
		    "message": "Item has been added to cart"
		  }
		])

	def get(self, request):
		user = request.user
		cart, exists = Cart.objects.get_or_create(user=user)
		return cart.items.all()

	def fetch_product_info(self, product_id):
		product_api_endpoint = f'{settings.API_URL}/product/{product_id}'
		resp = requests.get(product_api_endpoint).json()
		product = resp.get("product")
		prod, exists = Product.objects.get_or_create(**product)
		return prod
