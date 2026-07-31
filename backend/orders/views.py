from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from .models import Order, OrderItem, OrderStatusHistory
from .serializers import OrderSerializer, OrderCreateSerializer, OrderListSerializer
from cart.models import Cart


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for orders."""
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Order.objects.filter(user=user)
        # For anonymous users, use session-based filtering
        session_key = self.request.session.session_key
        return Order.objects.filter(session_key=session_key)

    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def get_permissions(self):
        if self.action in ['retrieve', 'list']:
            return [AllowAny()]
        return [AllowAny()]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create order from cart."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        cart_id = data.get('cart_id')

        # Get cart
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id, session_key=request.session.session_key)
            except Cart.DoesNotExist:
                cart = None
        else:
            cart = Cart.objects.filter(session_key=request.session.session_key).first()

        # Create order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key,
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data['phone'],
            city=data.get('city', ''),
            address=data.get('address', ''),
            postal_code=data.get('postal_code', ''),
            payment_method=data.get('payment_method', 'cash'),
            delivery_type=data.get('delivery_type', 'pickup'),
            comment=data.get('comment', ''),
        )

        # Add items from cart
        if cart:
            for cart_item in cart.items.select_related('product'):
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    product_sku=cart_item.product.sku or cart_item.product.article,
                    variant_name=cart_item.variant.name if cart_item.variant else '',
                    quantity=cart_item.quantity,
                    price=cart_item.price,
                )
            order.calculate_totals()
            cart.delete()

        # Add initial status
        OrderStatusHistory.objects.create(
            order=order,
            status='pending',
            comment='Заказ создан',
        )

        return Response(
            OrderSerializer(order, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['get'])
    def cancel(self, request, pk=None):
        """Cancel order."""
        order = self.get_object()
        if order.status in ['shipped', 'delivered', 'cancelled']:
            return Response(
                {'error': 'Невозможно отменить заказ в текущем статусе'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = 'cancelled'
        order.save()

        OrderStatusHistory.objects.create(
            order=order,
            status='cancelled',
            comment='Заказ отменён пользователем',
            created_by=request.user if request.user.is_authenticated else None,
        )

        return Response(OrderSerializer(order, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def by_email(self, request):
        """Get orders by email (for anonymous users)."""
        email = request.query_params.get('email')
        if not email:
            return Response({'error': 'Email обязателен'}, status=status.HTTP_400_BAD_REQUEST)

        orders = Order.objects.filter(email=email).order_by('-created_at')
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)
