from rest_framework import serializers
from .models import Category, Brand, Product, ProductImage, ProductSpecification, ProductVariant


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'parent', 'children',
            'description', 'image', 'is_active', 'order',
            'meta_title', 'meta_description', 'product_count'
        ]

    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        return CategorySerializer(children, many=True).data

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class CategoryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for category lists."""
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image']


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'logo', 'description', 'website']


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'alt_text', 'is_main', 'order']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class ProductSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpecification
        fields = ['id', 'name', 'value']


class ProductVariantSerializer(serializers.ModelSerializer):
    final_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'sku', 'price_modifier', 'stock', 'attributes', 'is_active', 'final_price']


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product lists."""
    brand_name = serializers.CharField(source='brand.name', read_only=True, default=None)
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    main_image = serializers.SerializerMethodField()
    discount_percent = serializers.IntegerField(read_only=True)
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'article', 'brand', 'brand_name',
            'category', 'category_name', 'short_description', 'price',
            'old_price', 'discount_percent', 'stock', 'in_stock',
            'is_featured', 'is_bestseller', 'is_new', 'main_image'
        ]

    def get_main_image(self, obj):
        main_image = obj.images.filter(is_main=True).first()
        if main_image:
            request = self.context.get('request')
            if request and main_image.image:
                return request.build_absolute_uri(main_image.image.url)
            return main_image.image.url if main_image.image else None
        first_image = obj.images.first()
        if first_image and first_image.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_image.image.url)
            return first_image.image.url
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for product page."""
    brand = BrandSerializer(read_only=True)
    category = CategoryListSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    specifications = ProductSpecificationSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    discount_percent = serializers.IntegerField(read_only=True)
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'article', 'brand', 'category',
            'description', 'short_description', 'price', 'old_price',
            'discount_percent', 'stock', 'sku', 'barcode', 'weight',
            'dimensions', 'is_active', 'is_featured', 'is_bestseller',
            'is_new', 'created_at', 'updated_at', 'meta_title',
            'meta_description', 'images', 'specifications', 'variants', 'in_stock'
        ]
