from django.urls import path
from django.urls.conf import include
from django.views.generic.base import View
from . import views
from rest_framework_nested import routers


parent_router = routers.DefaultRouter()
parent_router.register('products', views.ProductViewSet, basename='products')
parent_router.register('collections', views.CollectionViewSet, basename='collection')
parent_router.register('carts', views.CartViewSet, basename= 'carts')

products_router = routers.NestedDefaultRouter(parent_router, 'products', lookup='product') #this is where product_pk created in kward
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')

cart_router = routers.NestedDefaultRouter(parent_router, 'carts', lookup = 'cart')
cart_router.register('items', views.CartItemViewSet, basename='cart-items')

# URLConf
urlpatterns = parent_router.urls + products_router.urls + cart_router.urls
