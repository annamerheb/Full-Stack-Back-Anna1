from rest_framework import viewsets, permissions, filters
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework_xml.parsers import XMLParser
from rest_framework_xml.renderers import XMLRenderer

from django_filters.rest_framework import DjangoFilterBackend

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
)

from .models import Product
from .serializers import ProductSerializer


@extend_schema_view(
    list=extend_schema(
        tags=["Products"],
        summary="Lister les produits",
        description="Supporte pagination (?page=) et tri (?ordering=price, -created_at, name).",
        responses={
            200: OpenApiResponse(response=ProductSerializer(many=True)),
        },
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
                value={"id": 1, "name": "Pencil", "price": "1.99", "created_at": "2025-01-01T12:00:00Z"},
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
