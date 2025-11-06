from django.db.models import Avg, Count, FloatField
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, permissions, filters, response, decorators, status
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework_xml.parsers import XMLParser
from rest_framework_xml.renderers import XMLRenderer

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
)

from .models import Product, Review
from .serializers import ProductSerializer, ReviewSerializer
from .permissions import IsOwnerOrReadOnly


@extend_schema_view(
    list=extend_schema(
        tags=["Products"],
        summary="Lister les produits",
        description="Supporte pagination (?page=) et tri (?ordering=price, -created_at, name).",
        responses={200: OpenApiResponse(response=ProductSerializer(many=True))},
        parameters=[
            OpenApiParameter(
                name="ordering",
                description="Tri (ex: price, -created_at, name)",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="name",
                description="Filtrer par nom (égalité exacte)",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="price",
                description="Filtrer par prix (égalité exacte)",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
             OpenApiParameter( 
                name="min_rating", 
                description="Filtrer par note moyenne minimale", 
                required=False, 
                type=float, 
                location=OpenApiParameter.QUERY, 
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=["Products"],
        summary="Détail produit",
        responses={200: OpenApiResponse(response=ProductSerializer)},
    ),
    create=extend_schema(
        tags=["Products"],
        summary="Créer un produit",
        request={
            "application/json": ProductSerializer,
            "application/xml": ProductSerializer,
        },
        responses={201: OpenApiResponse(response=ProductSerializer)},
        examples=[
            OpenApiExample(
                "Exemple de création (JSON)",
                value={"name": "Pencil", "price": "1.99"},
                request_only=True,
                media_type="application/json",
            ),
            OpenApiExample(
                "Exemple de réponse",
                value={
                    "id": 1,
                    "name": "Pencil",
                    "price": "1.99",
                    "created_at": "2025-01-01T12:00:00Z",
                },
                response_only=True,
                media_type="application/json",
            ),
        ],
    ),
    update=extend_schema(
        tags=["Products"],
        summary="Mettre à jour un produit",
        request={
            "application/json": ProductSerializer,
            "application/xml": ProductSerializer,
        },
        responses={200: OpenApiResponse(response=ProductSerializer)},
    ),
    partial_update=extend_schema(
        tags=["Products"],
        summary="Modifier partiellement un produit",
        request={
            "application/json": ProductSerializer,
            "application/xml": ProductSerializer,
        },
        responses={200: OpenApiResponse(response=ProductSerializer)},
    ),
    destroy=extend_schema(
        tags=["Products"],
        summary="Supprimer un produit",
        responses={204: OpenApiResponse(description="No Content")},
    ),
)
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # Accept JSON & XML; render JSON & XML
    parser_classes = [JSONParser, XMLParser]
    renderer_classes = [JSONRenderer, XMLRenderer]

    # Filtering / ordering
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ["created_at", "price", "name"]
    ordering = ["-created_at"]
    filterset_fields = ["name", "price"]

    def get_queryset(self):
        qs = super().get_queryset()

        # Annotate average rating and number of reviews
        qs = qs.annotate(
            avg_rating=Coalesce(
                Avg("reviews__rating"), 0.0, output_field=FloatField()
            ),
            reviews_count=Count("reviews"),
        )

        # Filter by ?min_rating=
        min_rating = self.request.query_params.get("min_rating")
        if min_rating:
            try:
                qs = qs.filter(avg_rating__gte=float(min_rating))
            except ValueError:
                pass

        return qs

    @extend_schema(
        summary="Obtenir les statistiques de notation d’un produit",
        description="Retourne la note moyenne et le nombre total d’avis du produit.",
    )
    @decorators.action(detail=True, methods=["get"], url_path="rating")
    def rating(self, request, pk=None):
        product = self.get_object()
        data = {
            "product_id": product.id,
            "avg_rating": getattr(product, "avg_rating", None)
            or product.reviews.aggregate(avg=Avg("rating"))["avg"]
            or 0.0,
            "count": product.reviews.count(),
        }
        return response.Response(data)

    @extend_schema(
        summary="Lister les avis d’un produit",
        description="Retourne tous les avis associés à un produit, triés du plus récent au plus ancien.",
    )
    @decorators.action(detail=True, methods=["get"], url_path="reviews")
    def product_reviews(self, request, pk=None):
        product = self.get_object()
        qs = product.reviews.all().order_by("-created_at")
        ser = ReviewSerializer(qs, many=True)
        return response.Response(ser.data)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related("product", "user").all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
