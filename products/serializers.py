from rest_framework import serializers
from .models import Product, Review


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # affiche le username

    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ("user", "created_at")

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("La note doit être entre 1 et 5.")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        if request and request.method == "POST":
            product = attrs.get("product")
            # 1 seul avis par user (déjà garanti par Meta + validation côté view)
            if product and Review.objects.filter(product=product, user=request.user).exists():
                raise serializers.ValidationError("Vous avez déjà laissé un avis pour ce produit.")
            # Empêcher d’évaluer son propre produit si Product.owner est défini
            if product and getattr(product, "owner_id", None) == getattr(request.user, "id", None):
                raise serializers.ValidationError("Vous ne pouvez pas évaluer votre propre produit.")
        return attrs


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
