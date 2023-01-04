from .views import *
from django.urls import path

urlpatterns=[
    path("",HomeView.as_view(),name="home"),
    path("category/<slug>", CategoryView.as_view(), name="category"),
    path("search", SearchView.as_view(), name="search"),
    path("brand/<slug>", BrandView.as_view(), name="brand"),
    path("details/<slug>", ProductDetailView.as_view(), name="details"),
    path("signup",signup,name="signup"),
    path("product_review/<slug>", product_review, name="product_review"),
    path("cart/<slug>",cart,name="cart"),
    path("my_cart",CartView.as_view(),name="my_cart"),
    path("reduce_cart/<slug>", decrease_quantity, name="reduce_cart"),
    path("delete_cart/<slug>", delete_cart, name="delete_cart"),
]