from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from products.models import Product, Review

User = get_user_model()


class ReviewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")
        self.product = Product.objects.create(name="Stylo", price="2.50")
        self.client.force_authenticate(user=self.user)

    def test_create_review_once(self):
        res1 = self.client.post(
            "/api/reviews/",
            {"product": self.product.id, "rating": 5, "comment": "Top"},
            format="json",
        )
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED, res1.content)

        res2 = self.client.post(
            "/api/reviews/",
            {"product": self.product.id, "rating": 4},
            format="json",
        )
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_product_rating_endpoint(self):
        Review.objects.create(product=self.product, user=self.user, rating=4)
        res = self.client.get(f"/api/products/{self.product.id}/rating/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("avg_rating", res.data)

    def test_filter_products_by_min_rating(self):
        Review.objects.create(product=self.product, user=self.user, rating=5)
        res = self.client.get("/api/products/?min_rating=4")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(any(p["id"] == self.product.id for p in res.data["results"]))
