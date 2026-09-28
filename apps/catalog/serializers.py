from rest_framework import serializers
from apps.catalog.models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'image')

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'description', 'price', 'sale_price', 'stock', 'image', 'image_url', 'is_active', 'rating', 'review_count', 'category_id', 'category_name')
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return 'https://via.placeholder.com/300x300?text=Product'
