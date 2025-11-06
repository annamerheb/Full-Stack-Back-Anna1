$1

> **Pré-requis macOS (optionnel mais recommandé)**
>
> ```bash
> # Installer Homebrew si absent
> /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
>
> # Outils utiles
> brew update && brew upgrade
> brew install python jq sqlite
> ```

---

## 0) Préparer l’environnement

```bash
# Activer le venv et installer
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt

# Migrations + superuser
make makemigrations
make migrate
python manage.py createsuperuser

# Lancer le serveur dev
make run
# -> http://127.0.0.1:8000
```

Optionnel : installe `jq` pour formater les réponses JSON.

```bash
brew install jq
```

---

## 1) Obtenir un JWT (écriture protégée)

```bash
# Remplacer USER/PASS par vos identifiants superuser
curl -s -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"USER","password":"PASS"}' | tee /tmp/token.json

# Export du token Access (nécessite jq)
export TOKEN=$(jq -r .access /tmp/token.json)
```

> Sans `jq`, ouvrez `/tmp/token.json`, copiez la valeur de `access` et faites :
>
> ```bash
> export TOKEN=COLLER_ICI
> ```

---

## 2) Sanity check — endpoints et docs

```bash
# Ping liste produits (JSON)
curl -H "Accept: application/json" http://127.0.0.1:8000/api/products/ | jq .

# Ping liste produits (XML)
curl -H "Accept: application/xml" http://127.0.0.1:8000/api/products/

# Docs (ouvrir dans le navigateur)
# Swagger: http://127.0.0.1:8000/api/docs/
# ReDoc:   http://127.0.0.1:8000/api/redoc/
```

---

## 3) CRÉATION — Alimenter en **JSON** (réponses JSON)

```bash
curl -X POST http://127.0.0.1:8000/api/products/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -d '{"name":"Pencil","price":"1.99"}' | jq .

curl -X POST http://127.0.0.1:8000/api/products/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -d '{"name":"Notebook","price":"3.50"}' | jq .

curl -X POST http://127.0.0.1:8000/api/products/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -d '{"name":"Eraser","price":"0.99"}' | jq .
```

### Boucle — 10 items JSON

```bash
for n in {1..10}; do
  price=$(awk -v min=1 -v max=20 'BEGIN{srand(); printf "%.2f", min+rand()*(max-min)}')
  curl -s -X POST http://127.0.0.1:8000/api/products/ \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" -H "Accept: application/json" \
    -d "{\"name\":\"Item$n\",\"price\":\"$price\"}" > /dev/null
  echo "> created Item$n $price"
done
```

---

## 4) CRÉATION — Alimenter en **XML** (réponses XML/JSON)

```bash
# XML -> réponse XML
curl -X POST http://127.0.0.1:8000/api/products/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/xml" -H "Accept: application/xml" \
  -d '<root><name>Marker</name><price>2.20</price></root>'

# XML -> réponse JSON
curl -X POST http://127.0.0.1:8000/api/products/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/xml" -H "Accept: application/json" \
  -d '<root><name>Ruler</name><price>1.50</price></root>' | jq .
```

### Boucle — 5 items XML

```bash
for n in {1..5}; do
  curl -s -X POST http://127.0.0.1:8000/api/products/ \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/xml" -H "Accept: application/xml" \
    -d "<root><name>XMLItem$n</name><price>$((n+1)).75</price></root>" > /dev/null
  echo "> created XMLItem$n"
done
```

---

## 5) LISTE — Pagination, tri, filtres

```bash
# JSON
curl -H "Accept: application/json" \
  "http://127.0.0.1:8000/api/products/?page=1&ordering=-created_at" | jq .

# XML
curl -H "Accept: application/xml" \
  "http://127.0.0.1:8000/api/products/?ordering=price"

# Filtres exacts (name, price)
curl -H "Accept: application/json" \
  "http://127.0.0.1:8000/api/products/?name=Pencil" | jq .

curl -H "Accept: application/json" \
  "http://127.0.0.1:8000/api/products/?price=3.50" | jq .
```

---

## 6) DÉTAIL — GET, PUT, PATCH, DELETE

> Remplacer `:id` par un ID existant (voir liste précédente).

### GET

```bash
curl -H "Accept: application/json" http://127.0.0.1:8000/api/products/1/ | jq .
```

### PUT (full update)

```bash
# JSON
curl -X PUT http://127.0.0.1:8000/api/products/1/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -d '{"name":"Pencil","price":"2.49"}' | jq .

# XML
curl -X PUT http://127.0.0.1:8000/api/products/2/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/xml" -H "Accept: application/xml" \
  -d '<root><name>Notebook</name><price>3.90</price></root>'
```

### PATCH (partial update)

```bash
curl -X PATCH http://127.0.0.1:8000/api/products/1/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -d '{"price":"2.99"}' | jq .
```

### DELETE

```bash
curl -X DELETE http://127.0.0.1:8000/api/products/3/ \
  -H "Authorization: Bearer $TOKEN" -i
# -> HTTP/1.1 204 No Content
```

---

## 7) Jeux de données « volumineux »

### 7.1 30 produits JSON aléatoires

```bash
for n in {1..30}; do
  price=$(awk -v min=0.5 -v max=50 'BEGIN{srand(); printf "%.2f", min+rand()*(max-min)}')
  curl -s -X POST http://127.0.0.1:8000/api/products/ \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" -H "Accept: application/json" \
    -d "{\"name\":\"Load$n\",\"price\":\"$price\"}" > /dev/null
  if (( n % 5 == 0 )); then echo "> $n produits créés"; fi
done
```

### 7.2 10 produits XML

```bash
for n in {1..10}; do
  curl -s -X POST http://127.0.0.1:8000/api/products/ \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/xml" -H "Accept: application/xml" \
    -d "<root><name>XMLBulk$n</name><price>$((n*2)).00</price></root>" > /dev/null
  if (( n % 5 == 0 )); then echo "> $n produits XML créés"; fi
done
```

---

## 8) Vérifier dans SQLite

```bash
sqlite3 db.sqlite3 "SELECT COUNT(*) FROM products_product;"
sqlite3 db.sqlite3 "SELECT id, name, price, created_at FROM products_product ORDER BY id DESC LIMIT 15;"
```

> Dans DBeaver : Tables → `products_product` → `SELECT * FROM products_product ORDER BY id DESC;`

---

## 9) Cas d’erreurs à tester (utile pour QA)

```bash
# Prix invalide (0) -> 400
curl -X POST http://127.0.0.1:8000/api/products/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -d '{"name":"Bad","price":"0"}' | jq .

# Sans token -> 401 sur POST
curl -X POST http://127.0.0.1:8000/api/products/ \
  -H "Content-Type: application/json" \
  -d '{"name":"NoAuth","price":"9.99"}' -i

# Content-Type non supporté -> 415
curl -X POST http://127.0.0.1:8000/api/products/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: text/plain" \
  -d 'name=Weird&price=1.23' -i
```

---

## 10) Export du schéma OpenAPI

```bash
make schema-json   # JSON
make schema-yaml   # YAML
```

---

## 11) Raccourcis utiles

```bash
# Top 10 par prix décroissant (JSON)
curl -s "http://127.0.0.1:8000/api/products/?ordering=-price" -H "Accept: application/json" | jq '.count, .results[0:10]'

# Première page triée par date descendante (XML)
curl -s "http://127.0.0.1:8000/api/products/?ordering=-created_at" -H "Accept: application/xml"
```

---

### À retenir

* **JSON & XML** sont des formats **d’échange** : l’API parse → valide → **enregistre en colonnes** (pas en JSON/XML) ; la réponse est rendue selon `Accept`.
* **JWT** requis pour l’écriture (utiliser `Authorization: Bearer $TOKEN`).
* Toujours préciser **Content-Type** (ce qu’on envoie) et **Accept** (ce qu’on veut en réponse).
