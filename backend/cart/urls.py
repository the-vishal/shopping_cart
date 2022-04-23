from django.urls import re_path
from django.conf import settings
from cart.views import AddItemView, ListItemsView, CheckOutView


urlpatterns = [
    re_path(r'item$', AddItemView.as_view()),
    re_path(r'items$', ListItemsView.as_view()),
    re_path(r'checkout-value$', CheckOutView.as_view()),
]
