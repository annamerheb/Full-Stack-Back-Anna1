# Authentification JWT (SimpleJWT)

## Obtenir un token
POST /api/auth/token/
Body (JSON): { "username": "<admin>", "password": "<motdepasse>" }

## Rafraîchir
POST /api/auth/token/refresh/
Body (JSON): { "refresh": "<refresh_token>" }

## Utilisation
Ajouter l'en-tête:
Authorization: Bearer <access_token>

### Exemples curl
```bash
# 1) Obtenir tokens
curl -s -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"<motdepasse>"}'

# 2) Créer un produit (auth requis)
curl -s -X POST http://127.0.0.1:8000/api/products/ \
  -H "Authorization: Bearer <ACCESS>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Notebook","price":"4.20"}'

# 3) Lecture publique (pas besoin de token)
curl -s http://127.0.0.1:8000/api/products/
