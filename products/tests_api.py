from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status


User = get_user_model()


class ProductXMLJSONTests(APITestCase):
    def setUp(self):
        # Create a user and authenticate the test client
        self.user = User.objects.create_user(username="a", password="a")
        # Force-authenticate: bypasses auth backend (perfect for unit tests)
        self.client.force_authenticate(user=self.user)

    def test_create_product_json(self):
        res = self.client.post(
            "/api/products/",
            data={"name": "Pencil", "price": "1.99"},
            format="json",
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.content)
        self.assertEqual(res.data["name"], "Pencil")

    def test_create_product_xml(self):
        xml_body = "<root><name>Notebook</name><price>3.50</price></root>"
        res = self.client.post(
            "/api/products/",
            data=xml_body,
            content_type="application/xml",
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.content)
        self.assertEqual(res.data["name"], "Notebook")

    def test_list_products_as_xml(self):
        # seed one row
        self.client.post(
            "/api/products/",
            data={"name": "Eraser", "price": "0.99"},
            format="json",
            HTTP_ACCEPT="application/json",
        )
        # request XML
        res = self.client.get("/api/products/", HTTP_ACCEPT="application/xml")
        self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
        self.assertIn(b"<?xml", res.content[:20])
