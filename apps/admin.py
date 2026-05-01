from django.contrib import admin
from django.template.defaulttags import comment

from apps.models import ProductImage, Product, Category, Review


class ProductImageInline(admin.StackedInline):
    model = ProductImage
    min_num = 1
    extra = 0


@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'shipping_cost', 'discount')
    inlines = [ProductImageInline]


@admin.register(Category)
class CategoryModelAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Review)
class ReviewModelAdmin(admin.ModelAdmin):
    list_display = ('title', 'comment')

