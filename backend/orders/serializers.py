from rest_framework import serializers
from .models import Order, OrderItem, OrderStatusHistory


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_sku',
            'variant_name', 'quantity', 'price', 'total'
        ]


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = OrderStatusHistory
        fields = ['id', 'status', 'comment', 'created_by', 'created_by_name', 'created_at']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f'{obj.created_by.first_name} {obj.created_by.last_name}'.strip() or obj.created_by.username
        return None


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'first_name', 'last_name', 'email', 'phone',
            'city', 'address', 'postal_code', 'status', 'payment_method',
            'delivery_type', 'subtotal', 'delivery_cost', 'total', 'discount',
            'comment', 'admin_comment', 'tracking_number',
            'created_at', 'updated_at', 'confirmed_at', 'shipped_at', 'delivered_at',
            'items', 'status_history'
        ]
        read_only_fields = ['id', 'status', 'subtotal', 'delivery_cost', 'total', 'discount',
                          'created_at', 'updated_at', 'confirmed_at', 'shipped_at', 'delivered_at']


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating order from cart."""
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    city = serializers.CharField(max_length=200, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    postal_code = serializers.CharField(max_length=10, required=False, allow_blank=True)
    payment_method = serializers.ChoiceField(
        choices=['cash', 'card', 'online'],
        default='cash'
    )
    delivery_type = serializers.ChoiceField(
        choices=['pickup', 'courier', 'cdek'],
        default='pickup'
    )
    comment = serializers.CharField(required=False, allow_blank=True)
    cart_id = serializers.CharField(required=False)


class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for order list."""
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone',
            'status', 'total', 'items_count', 'created_at'
        ]

    def get_items_count(self, obj):
        return obj.items.count()
