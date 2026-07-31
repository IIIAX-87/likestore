from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from .models import Cart, CartItem, Wishlist
from .serializers import (
    CartSerializer, CartAddItemSerializer, WishlistSerializer
)
from products.models import Product, ProductVariant


class CartViewSet(viewsets.GenericViewSet):
    """ViewSet for shopping cart."""
    serializer_class = CartSerializer
    permission_classes = [AllowAny]

    def get_cart(self):
        """Get or create cart for current session/user."""
        if self.request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=self.request.user)
        else:
            session_key = self.request.session.session_key
            if not session_key:
                self.request.session.create()
                session_key = self.request.session.session_key
            cart, _ = Cart.objects.get_or_create(session_key=session_key)
        return cart

    def get_queryset(self):
        return [self.get_cart()]

    def list(self, request):
        """Get current cart."""
        cart = self.get_cart()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def add_item(self, request):
        """Add item to cart."""
        serializer = CartAddItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        variant_id = serializer.validated_data.get('variant_id')
        quantity = serializer.validated_data['quantity']

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        cart = self.get_cart()

        # Get variant if specified
        variant = None
        price = product.price
        if variant_id:
            try:
                variant = ProductVariant.objects.get(id=variant_id, product=product)
                price = variant.final_price
            except ProductVariant.DoesNotExist:
                pass

        # Check if item already in cart
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product, variant=variant)
            cart_item.quantity += quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                variant=variant,
                quantity=quantity,
                price=price
            )

        return Response(CartSerializer(cart, context={'request': request}).data)

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def update_item(self, request):
        """Update cart item quantity."""
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity', 1)

        if not item_id:
            return Response({'error': 'Item ID required'}, status=status.HTTP_400_BAD_REQUEST)

        cart = self.get_cart()

        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()

        return Response(CartSerializer(cart, context={'request': request}).data)

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def remove_item(self, request):
        """Remove item from cart."""
        item_id = request.data.get('item_id')

        if not item_id:
            return Response({'error': 'Item ID required'}, status=status.HTTP_400_BAD_REQUEST)

        cart = self.get_cart()

        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(CartSerializer(cart, context={'request': request}).data)

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def clear(self, request):
        """Clear cart."""
        cart = self.get_cart()
        cart.items.all().delete()
        return Response(CartSerializer(cart, context={'request': request}).data)


class WishlistViewSet(viewsets.GenericViewSet):
    """ViewSet for wishlist."""
    serializer_class = WishlistSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Wishlist.objects.filter(user=self.request.user)
        session_key = self.request.session.session_key
        return Wishlist.objects.filter(session_key=session_key)

    def get_query_params(self):
        """Get session key for anonymous users."""
        if self.request.user.is_authenticated:
            return {'user': self.request.user}
        session_key = self.request.session.session_key
        if not session_key:
            self.request.session.create()
            session_key = self.request.session.session_key
        return {'session_key': session_key}

    def list(self, request):
        """Get wishlist items."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add(self, request):
        """Add product to wishlist."""
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'error': 'Product ID required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        params = self.get_query_params()
        wishlist_item, created = Wishlist.objects.get_or_create(
            product=product,
            defaults=params
        )

        return Response({
            'added': created,
            'item': WishlistSerializer(wishlist_item).data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def remove(self, request):
        """Remove product from wishlist."""
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'error': 'Product ID required'}, status=status.HTTP_400_BAD_REQUEST)

        params = self.get_query_params()
        deleted, _ = Wishlist.objects.filter(product_id=product_id, **params).delete()

        return Response({'removed': deleted > 0})

    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear wishlist."""
        queryset = self.get_queryset()
        count = queryset.count()
        queryset.delete()
        return Response({'cleared': count})
