from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.http import  HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import generate_code
from django.views import View
from django.views.generic import ListView, DetailView, CreateView

from .forms import RegisterUserModelForm
from .models import Product, Category, Cart, EmailVerify
from django.db.models import Q

from .tasks import send_to_email


class CategoryMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProductListView(CategoryMixin, ListView):
    model = Product
    template_name = 'apps/test_list_page.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = Product.objects.all()

        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        max_price = self.request.GET.get('max_price')
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(description__icontains=q)
            )

        return queryset


class ProductDetailView(CategoryMixin, DetailView):
    model = Product
    template_name = 'apps/test_detail_page.html'
    context_object_name = 'product'


def register(request):
    return render(request, 'auth/register.html')


class ShoppingCartListView(CategoryMixin, LoginRequiredMixin, ListView):
    queryset = Cart.objects.all()
    template_name = 'apps/shopping_cart.html'
    context_object_name = 'carts'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        user = self.request.user

        total_price = 0
        total_count = 0
        total_discount = 0
        total_discount_price = 0
        total_shipping = 0

        for cart in user.carts.all():
            total_price += cart.product.current_price * cart.quantity
            total_count += cart.quantity
            total_discount = cart.product.discount * total_count

            discount_amount = cart.product.price * cart.product.discount / 100
            total_discount_price += discount_amount * cart.quantity
            total_shipping += cart.product.shipping_cost * cart.quantity

        context['total_price'] = total_price
        context['total_count'] = total_count
        context['total_discount'] = total_discount
        context['total_discount_price'] = total_discount_price
        context['total_shipping'] = total_shipping

        return context


class AddCartView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, pk=pk)
        print("ADD CART WORKED")

        cart, created = Cart.objects.get_or_create(
            user=request.user,
            product=product
        )

        if not created:
            cart.quantity += 1
            cart.save()

        return redirect(request.META.get('HTTP_REFERER', '/'))


class CustomLoginView(LoginView):
    template_name = 'auth/login.html'
    next_page = reverse_lazy('test_list_page')


class CustomRegisterView(CreateView):
    queryset = User.objects.all()
    template_name = 'auth/register.html'
    form_class = RegisterUserModelForm
    success_url = reverse_lazy('test_list_page')

    def form_invalid(self, form):
        return super().form_invalid(form)

    def form_valid(self, form):
        self.object = form.save()
        self.request.session['user_id'] = self.object.id
        code = generate_code()
        EmailVerify.objects.update_or_create(user=self.object, defaults={' code':code})
        send_to_email.delay(self.object.email, self.object.first_name, code)
        return redirect('verify')


class RemoveProductView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        Cart.objects.filter(pk=pk).delete()
        return redirect("shopping_cart_page")


class CheckoutView(ListView):
    template_name = 'apps/checkout.html'
    context_object_name = 'carts'

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        carts = context['carts']
        total_price = 0
        total_count = 0
        total_shipping = 0

        for cart in carts.all():
            total_price += cart.product.current_price * cart.quantity
            total_count += cart.quantity
            total_shipping += cart.product.shipping_cost * cart.quantity

        context['total_price'] = total_price
        context['total_count'] = total_count
        context['total_shipping'] = total_shipping

        return context



class VerifyView(View):
    template_name = 'apps/verify.html'

    def post(self, request, *args, **kwargs):
        code = request.POST.get('code')

        user_id = request.session.get('user_id')

        try:
            verification = EmailVerify.objects.get(user_id=user_id, code=code)
        except EmailVerify.DoesNotExist:
            return HttpResponse("Kod noto‘g‘ri ❌")

        if verification.is_expired():
            return HttpResponse("Kod eskirgan ❌")

        verification.user.is_active = True
        verification.user.save()

        return redirect('login')
