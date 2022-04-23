from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


import requests
from bisect import bisect
from django.conf import settings
from cart.models import Product, CartItem, Cart
from cart.serializers import CartItemSerializer

class AddItemView(APIView):
    permissions_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )

    def post(self, request):
        data = request.data
        pid = data.get('product_id')
        qty = data.get('quantity')
        user = request.user

        cart, exists = Cart.objects.get_or_create(user=user)
        status = "error"
        message = "Invalid product id"
        code = 400
        product = self.fetch_product_info(pid)
        if product:
            citem = CartItem.objects.create(product=product, quantity=qty)
            cart.items.add(citem)
            status = "success"
            message = "Item has been added to cart"
            code = 200
        return Response([{
            "status": status,
            "message": message}
        ], code)

    def fetch_product_info(self, product_id):
        prod = Product.objects.filter(id=product_id).first()
        if not prod:
            product_api_endpoint = f'{settings.API_URL}/product/{product_id}'
            resp = requests.get(product_api_endpoint).json()
            product = resp.get("product")
            if product:
                prod, exists = Product.objects.get_or_create(**product)
        return prod


class ListItemsView(generics.ListAPIView):
    permissions_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )
    serializer_class = CartItemSerializer

    EMPTY_CART = "empty_cart"
    def get_queryset(self):
        user = self.request.user
        cart = Cart.objects.get(user=user)
        return cart.items.all()

    def post(self, request):
        data = request.data
        action = data.get("action")
        status = "error"
        message ="Bad Request"
        code = 400
        if action == self.EMPTY_CART:
            user = request.user
            cart = Cart.objects.filter(user=user).first()
            if cart:
                cart.items.all().delete()
                status = "success"
                message ="All items have been removed from the cart !"
                code = 200
        return Response([
            {
                "status": status,
                "message": message
            }
        ], code)


class CheckOutView(APIView):
    permissions_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication, )

    def get(self, request):
        status = "error"
        message = "Invalid postal code, valid ones are 465535 to 465545."
        code = 400
        data = request.GET
        postal_code = data.get('postal_code')
        user = request.user
        cart = Cart.objects.filter(user=user).first()

        cost = 0.0
        if cart:
            products_cost, products_weight = self.get_products_cost_and_weight(cart)
            distance = self.get_checkout_distance(postal_code)
            shipping_charges = self.get_shipping_charges(products_weight, distance)
            cost = products_cost + shipping_charges
            code = 200
            status = "success"
            message = f"Total value of your shopping cart is - ${cost}"
        return Response([
            {
                "status": status,
                "message": message
            }
        ], code)


    def get_shipping_charges(self, weight, distance):
        weight_range = [0,2,5,20,10000000000]
        distance_range = [0,5,20,50,500,800,10000000000]

        price_map = [
            [12, 15, 20, 50, 100, 220],
            [14, 18, 24, 55, 110, 250],
            [16, 25, 30, 80, 130, 270],
            [21, 35, 50, 90, 150, 300]
        ]
        w = bisect(weight_range, weight) -1
        d = bisect(distance_range, distance) -1
        price = price_map[w][d]

        return price

    
    def get_products_cost_and_weight(self, cart):
       products_cost = 0
       products_weight = 0.0

       for item in cart.items.all():
           price = item.product.price
           disc = item.product.discount_percentage
           qty = item.quantity
           products_cost += qty*(price - (price*disc)/100)  
           products_weight += qty*(item.product.weight_in_grams/1000)
       return products_cost, products_weight


    def get_checkout_distance(self, pincode):
        distance_api_endpoint = f'{settings.API_URL}/warehouse/distance/?postal_code={pincode}'
        resp = requests.get(distance_api_endpoint).json()
        distance = resp.get("distance_in_kilometers")
       	return distance
