# API produits (Module 2)

Base: `http://127.0.0.1:8000/api/`

## Endpoints
- `GET /products/` (liste paginée, `?ordering=price` ou `?ordering=-name`)
- `POST /products/` (JSON: `{ "name": "...", "price": "1.99" }`)
- `GET /products/{id}/`
- `PATCH /products/{id}/` (ex: `{ "price": "2.49" }`)
- `DELETE /products/{id}/`

### Exemples curl
```bash
curl http://127.0.0.1:8000/api/products/
curl -X POST http://127.0.0.1:8000/api/products/ -H "Content-Type: application/json" -d '{"name":"Pencil","price":"1.99"}'
curl http://127.0.0.1:8000/api/products/1/
curl -X PATCH http://127.0.0.1:8000/api/products/1/ -H "Content-Type: application/json" -d '{"price":"2.49"}'
curl -X DELETE http://127.0.0.1:8000/api/products/1/


curl -X POST http://127.0.0.1:8000/api/products/ -H "Content-Type: application/json" -d '{"name":"Pencil","price":"1.99"}'
curl -X POST http://127.0.0.1:8000/api/products/ -H "Content-Type: application/json" -d '{"name":"Notebook","price":"3.50"}'
curl -X POST http://127.0.0.1:8000/api/products/ -H "Content-Type: application/json" -d '{"name":"Eraser","price":"0.99"}'
curl -X POST http://127.0.0.1:8000/api/products/ -H "Content-Type: application/json" -d '{"name":"Marker","price":"2.75"}'

curl http://127.0.0.1:8000/api/products/
curl "http://127.0.0.1:8000/api/products/?ordering=price"
curl "http://127.0.0.1:8000/api/products/?ordering=-price"
curl "http://127.0.0.1:8000/api/products/?ordering=name"
curl "http://127.0.0.1:8000/api/products/?ordering=-name"

curl -X POST http://127.0.0.1:8000/api/products/ -H "Content-Type: application/json" -d '{"name":"BigPrice","price":"10.00"}'
curl "http://127.0.0.1:8000/api/products/?ordering=price"
curl "http://127.0.0.1:8000/api/products/?ordering=-price"
