from datetime import timedelta

from django.db.models import Model, ForeignKey, CASCADE, JSONField, Q, ImageField, OneToOneField
from django.db.models.constraints import CheckConstraint
from django.db.models.fields import CharField, DecimalField, TextField, PositiveSmallIntegerField, PositiveIntegerField, \
    DateTimeField
from django.utils import timezone
from django.utils.timezone import now


class Category(Model):
    name = CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(Model):
    name = CharField(max_length=255)
    category = ForeignKey('apps.Category', CASCADE, related_name='products')
    description = TextField()
    specification = JSONField()
    price = DecimalField(max_digits=10, decimal_places=5)
    discount = PositiveSmallIntegerField(default=0, help_text='Chegirma(% foizda ')
    shipping_cost = PositiveIntegerField(default=0)
    like_count = PositiveIntegerField(default=0)
    quantity = PositiveIntegerField(default=0)
    created_at = DateTimeField(auto_now_add=True)

    @property
    def current_price(self):
        return self.price - self.price * self.discount / 100

    @property
    def is_new(self):
        return now() - self.created_at < timedelta(days=3)

    @property
    def is_stock(self):
        return self.quantity > 0

    # class Meta:
    #     constraints = [
    #         CheckConstraint(check=Q(discount__lte=100), name='check_product_price',
    #                         violation_error_message="chegirma  foizda (0-100 oraliqda bo'lishi kerak)"),
    #     ]

    def __str__(self):
        return self.name


class ProductImage(Model):
    image = ImageField(upload_to='products/%Y/%m/%d')
    product = ForeignKey('apps.Product', CASCADE, related_name='images')


class Cart(Model):
    user = ForeignKey('auth.User', CASCADE, related_name='carts')
    product = ForeignKey('apps.Product', CASCADE, related_name='items')
    quantity = PositiveIntegerField(db_default=1)

    class Meta:
        unique_together = ('user', 'product')


class Review(Model):
    title = CharField(max_length=255)
    comment = TextField()
    product = ForeignKey('apps.Product', CASCADE, related_name='reviews')
    author = ForeignKey('auth.User', CASCADE, related_name='reviews')
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class EmailVerify(Model):
    user = OneToOneField('auth.User', CASCADE)
    code = CharField(max_length=6)
    created_at = DateTimeField(auto_now_add=True)

    def is_expired(self):
        return self.created_at < timezone.now() - timedelta(minutes=5)
