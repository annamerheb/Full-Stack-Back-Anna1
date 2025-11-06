from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    """
    Représentation d'un produit vendable.
    - name: nom commercial
    - price: prix TTC en euros (doit être > 0)
    - created_at: horodatage de création (lecture seule)
    """
    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ("created_at",)

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le prix doit être > 0")
        return value
