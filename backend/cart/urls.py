from django.urls import re_path
from django.conf import settings
from cart.views import AddItemView


urlpatterns = [
    re_path(r'item$', AddItemView.as_view()),
    # re_path(r'items$', AddItemView.as_view()),
    # re_path(r'checkout-value$', AddItemView.as_view()),
]
