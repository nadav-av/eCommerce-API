from typing import ItemsView
from rest_framework import fields, serializers
from .models import Cart, CartItem, Product, Collection, Review
from decimal import Decimal


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']

    # readonly meaning that not using for creating or updating a collection
    products_count = serializers.IntegerField(read_only=True)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'inventory',
                  'unit_price', 'price_with_tax', 'collection']

    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')

    def calculate_tax(self, product: Product):
        return Decimal(product.unit_price * Decimal(1.17)).quantize(Decimal('1.00'))


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'description']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)


class CartProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','title', 'description']

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product','quantity', 'total_product_price']
        depth = 1

    product = CartProductSerializer()
    total_product_price = serializers.SerializerMethodField(method_name='get_total_price')

    def get_total_price(self, item: CartItem):
        return Decimal(item.product.unit_price * item.quantity).quantize(Decimal('1.00'))
        

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'created_at', 'cart_items', 'total_cart_price']
    id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    cart_items = CartItemSerializer(many = True, read_only = True)
    total_cart_price = serializers.SerializerMethodField()

    def get_total_cart_price(self, cart : Cart):
        sum = 0
        for item in cart.cart_items.all():
            sum += ((item.product.unit_price) * (item.quantity))
        
        return Decimal(sum).quantize(Decimal('1.00'))


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class AddCartItemSerializer(serializers.ModelSerializer):

    def validate_product_id(self,value):
        if not Product.objects.filter(pk = value).exists():
            raise serializers.ValidationError('No product with given id found')
        return value


    # def validate_quantity(self, quantity):
    #         product = Product.objects.get(id= self.data.product_id)
    #         if quantity > product.inventory:
    #             raise serializers.ValidationError('Out of stock')
    #         return quantity


    def save(self, **kwargs):
        u_product_id = self.validated_data['product_id']
        u_quantity = self.validated_data['quantity']
        current_cart_id = self.context['cart_id']
        #the cart id is not in the request, its in the url, so need to bring from views
        try:
            cart_item = CartItem.objects.get(cart_id=current_cart_id, product_id= u_product_id)
            cart_item.quantity += u_quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            new_cart_item = CartItem.objects.create(cart_id=current_cart_id, **self.validated_data)
            self.instance = new_cart_item
        
        product = Product.objects.get(id = u_product_id)
        product.inventory -= u_quantity
        product.save()

        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']


    product_id = serializers.IntegerField() #product_id declared at runtime so have to adress it explicitly

    