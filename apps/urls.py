from django.urls import path

from apps.views import ProductListView, ProductDetailView, register, AddCartView, ShoppingCartListView, CustomLoginView, \
    RemoveProductView, CheckoutView, VerifyView

urlpatterns = [
    path('', ProductListView.as_view(), name='test_list_page'),
    path('detail<int:pk>', ProductDetailView.as_view(), name='test_detail_page'),
    path('login', CustomLoginView.as_view(), name='login'),
    path('register', register, name='register'),
    path('add-cart/<int:pk>/', AddCartView.as_view(), name='add_cart_page'),
    path('shopping-cart', ShoppingCartListView.as_view(), name='shopping_cart_page'),
    path('remove-cart/<int:pk>', RemoveProductView.as_view(), name='remove_cart'),
    path('checkout', CheckoutView.as_view(), name='checkout_page'),
    path('verify/', VerifyView.as_view(), name='verify'),

]
