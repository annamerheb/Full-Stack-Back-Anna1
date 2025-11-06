# tests/test_reviews_bonus.py
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from products.models import Product, Review

User = get_user_model()


class ReviewBonusTests(APITestCase):
    def setUp(self):
        # Deux utilisateurs : un vendeur (owner) et un client
        self.owner = User.objects.create_user(username="owner", password="pw")
        self.client_user = User.objects.create_user(username="client", password="pw")

        # Produit appartenant au vendeur (owner)
        self.product = Product.objects.create(name="Stylo", price="2.50", owner=self.owner)

    def test_cannot_review_own_product(self):
        """Empêcher les avis sur son propre produit."""
        self.client.force_authenticate(user=self.owner)
        res = self.client.post(
            "/api/reviews/",
            {"product": self.product.id, "rating": 5, "title": "Top", "comment": "Excellent"},
            format="json",
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert "propre produit" in str(res.data).lower()

    def test_review_pagination_and_ordering(self):
        """Vérifie pagination + ordering sur ReviewViewSet."""
        self.client.force_authenticate(user=self.client_user)

        # Crée plusieurs avis (sur le même produit)
        for i in range(15):
            u = User.objects.create_user(username=f"u{i}", password="pw")
            Review.objects.create(product=self.product, user=u, rating=(i % 5) + 1, title=f"t{i}")

        # Page 1 (page_size=5)
        res1 = self.client.get("/api/reviews/?page=1&page_size=5&ordering=-rating")
        assert res1.status_code == status.HTTP_200_OK
        assert len(res1.data["results"]) == 5
        # Vérifie tri descendant par rating (le premier doit être 5 ou 4, selon modulo)
        ratings_page1 = [r["rating"] for r in res1.data["results"]]
        assert ratings_page1 == sorted(ratings_page1, reverse=True)

        # Page 2
        res2 = self.client.get("/api/reviews/?page=2&page_size=5&ordering=-rating")
        assert res2.status_code == status.HTTP_200_OK
        assert len(res2.data["results"]) == 5

    @override_settings(
        REST_FRAMEWORK={
            "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",),
            "DEFAULT_THROTTLE_CLASSES": ("rest_framework.throttling.ScopedRateThrottle",),
            "DEFAULT_THROTTLE_RATES": {"review-create": "2/min"},  # 2 créations par minute
        }
    )
    def test_create_throttling(self):
        """Throttling léger sur la création d’avis (scope review-create)."""
        self.client.force_authenticate(user=self.client_user)

        # Deux créations OK
        r1 = self.client.post("/api/reviews/", {"product": self.product.id, "rating": 5}, format="json")
        r2 = self.client.post("/api/reviews/", {"product": self.product.id, "rating": 4}, format="json")

        # Troisième doit être throttled
        r3 = self.client.post("/api/reviews/", {"product": self.product.id, "rating": 3}, format="json")

        assert r1.status_code in (status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST)  # peut échouer si doublon
        assert r2.status_code in (status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST)
        assert r3.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    def test_reviews_supports_xml(self):
        """Support XML : Accept application/xml sur la liste des reviews."""
        self.client.force_authenticate(user=self.client_user)
        # Crée au moins un avis pour que la réponse ait du contenu
        Review.objects.create(product=self.product, user=self.client_user, rating=5, title="ok")

        res = self.client.get(
            "/api/reviews/",
            HTTP_ACCEPT="application/xml",
        )
        assert res.status_code == status.HTTP_200_OK
        assert "application/xml" in res["Content-Type"].lower()
