from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Brand, Product
from .serializers import (
    CategorySerializer, CategoryListSerializer,
    BrandSerializer, ProductListSerializer, ProductDetailSerializer
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for categories."""
    queryset = Category.objects.filter(is_active=True, parent__isnull=True)
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = Category.objects.filter(is_active=True)
        parent_id = self.request.query_params.get('parent')
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        return queryset

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Return categories as nested tree."""
        root_categories = Category.objects.filter(is_active=True, parent__isnull=True)
        serializer = self.get_serializer(root_categories, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """Return products in category."""
        category = self.get_object()
        products = Product.objects.filter(category=category, is_active=True)
        
        # Apply filters
        brand = request.query_params.get('brand')
        if brand:
            products = products.filter(brand_id=brand)
        
        min_price = request.query_params.get('min_price')
        if min_price:
            products = products.filter(price__gte=min_price)
        
        max_price = request.query_params.get('max_price')
        if max_price:
            products = products.filter(price__lte=max_price)
        
        # Apply pagination
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for brands."""
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    lookup_field = 'slug'

    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """Return products of brand."""
        brand = self.get_object()
        products = Product.objects.filter(brand=brand, is_active=True)
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for products."""
    queryset = Product.objects.filter(is_active=True)
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'brand', 'is_featured', 'is_bestseller', 'is_new']
    search_fields = ['name', 'article', 'description']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Return featured products."""
        products = self.get_queryset().filter(is_featured=True)[:20]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def bestsellers(self, request):
        """Return bestsellers."""
        products = self.get_queryset().filter(is_bestseller=True)[:20]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def new(self, request):
        """Return new products."""
        products = self.get_queryset().filter(is_new=True)[:20]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search products."""
        query = request.query_params.get('q', '')
        if not query:
            return Response({'results': []})
        
        products = self.get_queryset().filter(name__icontains=query)[:20]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response({'results': serializer.data})

    @action(detail=True, methods=['get'])
    def related(self, request, slug=None):
        """Return related products."""
        product = self.get_object()
        products = self.get_queryset().filter(
            category=product.category
        ).exclude(id=product.id)[:10]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
