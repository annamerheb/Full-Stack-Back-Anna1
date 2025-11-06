# **alimenter massivement** la base et **déclencher tous les endpoints** (Windows PowerShell)

---

## 0) Préparer l’environnement

```powershell
# Créer et activer le venv
python -m venv .venv
. .\.venv\Scripts\Activate.ps1

# Installer les dépendances
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt

# Migrations + superuser
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Lancer le serveur dev
python manage.py runserver
# -> http://127.0.0.1:8000
```

Optionnel : installer `jq` pour formater le JSON.

```powershell
winget install jqlang.jq
# ou
choco install jq -y
```

---

## 1) Obtenir un JWT (écriture protégée)

```powershell
# Remplacer USER/PASS par vos identifiants superuser
$resp = Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:8000/api/auth/token/" `
  -ContentType "application/json" `
  -Body (@{ username = "USER"; password = "PASS" } | ConvertTo-Json)

# Export du token Access
$env:TOKEN = $resp.access
```

> Sans jq : ouvrez le fichier JSON avec Notepad, copiez la valeur `access` et faites :
>
> ```powershell
> $env:TOKEN = "COLLER_ICI"
> ```

---

## 2) Sanity check — endpoints et docs

```powershell
# Ping liste produits (JSON)
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/products/" -Headers @{Accept="application/json"} |
  ConvertTo-Json -Depth 10

# Ping liste produits (XML)
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/products/" -Headers @{Accept="application/xml"} |
  Select-Object -ExpandProperty Content

# Docs (ouvrir dans le navigateur)
Start-Process "http://127.0.0.1:8000/api/docs/"
Start-Process "http://127.0.0.1:8000/api/redoc/"
```

---

## 3) CRÉATION — Alimenter en **JSON** (réponses JSON)

```powershell
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/api/products/" `
  -Headers @{Authorization="Bearer $env:TOKEN";Accept="application/json"} `
  -ContentType "application/json" `
  -Body (@{name="Pencil";price="1.99"} | ConvertTo-Json) | ConvertTo-Json -Depth 10

Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/api/products/" `
  -Headers @{Authorization="Bearer $env:TOKEN";Accept="application/json"} `
  -ContentType "application/json" `
  -Body (@{name="Notebook";price="3.50"} | ConvertTo-Json) | ConvertTo-Json -Depth 10

Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/api/products/" `
  -Headers @{Authorization="Bearer $env:TOKEN";Accept="application/json"} `
  -ContentType "application/json" `
  -Body (@{name="Eraser";price="0.99"} | ConvertTo-Json) | ConvertTo-Json -Depth 10
```

### Boucle — 10 items JSON

```powershell
for ($n=1; $n -le 10; $n++) {
  $price = [math]::Round((Get-Random -Minimum 1.0 -Maximum 20.0), 2)
  $body = @{ name = "Item$n"; price = "$price" } | ConvertTo-Json
  Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/api/products/" `
    -Headers @{Authorization="Bearer $env:TOKEN";Accept="application/json"} `
    -ContentType "application/json" -Body $body | Out-Null
  Write-Host "> created Item$n $price"
}
```

---

## 4) CRÉATION — Alimenter en **XML** (réponses XML/JSON)

```powershell
# XML -> réponse XML
$xml = "<root><name>Marker</name><price>2.20</price></root>"
Invoke-WebRequest -Method POST -Uri "http://127.0.0.1:8000/api/products/" `
  -Headers @{Authorization="Bearer $env:TOKEN";Accept="application/xml"} `
  -ContentType "application/xml" -Body $xml |
  Select-Object -ExpandProperty Content

# XML -> réponse JSON
$xml = "<root><name>Ruler</name><price>1.50</price></root>"
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/api/products/" `
  -Headers @{Authorization="Bearer $env:TOKEN";Accept="application/json"} `
  -ContentType "application/xml" -Body $xml | ConvertTo-Json -Depth 10
```

### Boucle — 5 items XML

```powershell
for ($n=1; $n -le 5; $n++) {
  $xml = "<root><name>XMLItem$n</name><price>$($n+1).75</price></root>"
  Invoke-WebRequest -Method POST -Uri "http://127.0.0.1:8000/api/products/" `
    -Headers @{Authorization="Bearer $env:TOKEN";Accept="application/xml"} `
    -ContentType "application/xml" -Body $xml | Out-Null
  Write-Host "> created XMLItem$n"
}
```

---

## 5) LISTE — Pagination, tri, filtres

```powershell
# JSON
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/products/?page=1&ordering=-created_at" `
  -Headers @{Accept="application/json"} | ConvertTo-Json -Depth 10

# XML
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/products/?ordering=price" `
  -Headers @{Accept="application/xml"} | Select-Object -ExpandProperty Content

# Filtres exacts
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/products/?name=Pencil" `
  -Headers @{Accept="application/json"} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/products/?price=3.50" `
  -Headers @{Accept="application/json"} | ConvertTo-Json -Depth 10
```

---

## 6) DÉTAIL — GET, PUT, PATCH, DELETE

### GET

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/products/1/" `
  -Headers @{Accept="application/json"} | ConvertTo-Json -Depth 10
```

### PUT (full update)

```powershell
# JSON
Invoke-RestMethod -Method PUT -Uri "http://127.0.0.1:8000/api/products/1/" `
  -Headers @{Authorization="Bearer $env:TOKEN";Accept="application/json"} `
  -ContentType "application/json" `
  -Body (@{name="Pencil";price="2.49"} | ConvertTo-Json) | ConvertTo-Json -Depth 10

# XML
$xml = "<root><name>Notebook</name><price>3.90</price></root>"
Invoke-WebRequest -Method PUT -Uri "http://127.0.0.1:8000/api/products/2/" `
  -Headers @{Authorization="Bearer $env:TOKEN";Accept="application/xml"} `
  -ContentType "application/xml" -Body $xml |
  Select-Object -ExpandProperty Content
```

### PATCH

```powershell
Invoke-RestMethod -Method PATCH -Uri "http://127.0.0.1:8000/api/products/1/" `
  -Headers @{Authorization="Bearer $env:TOKEN";Accept="application/json"} `
  -ContentType "application/json" `
  -Body (@{price="2.99"} | ConvertTo-Json) | ConvertTo-Json -Depth 10
```

### DELETE

```powershell
Invoke-WebRequest -Method DELETE -Uri "http://127.0.0.1:8000/api/products/3/" `
  -Headers @{Authorization="Bearer $env:TOKEN"} -UseBasicParsing
# -> HTTP/1.1 204 No Content
```

---

## 7) Jeux de données « volumineux »

### 7.1 30 produits JSON aléatoires

```powershell
for ($n=1; $n -le 30; $n++) {
  $price = [math]::Round((Get-Random -Minimum 0.5 -Maximum 50.0), 2)
  $body = @{name="Load$n";price="$price"} | ConvertTo-Json
  Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/api/products/" `
    -Headers @{Authorization="Bearer $env:TOKEN";Accept="application/json"} `
    -ContentType "application/json" -Body $body | Out-Null
  if ($n % 5 -eq 0) { Write-Host "> $n produits créés" }
}
```

### 7.2 10 produits XML

```powershell
for ($n=1; $n -le 10; $n++) {
  $xml = "<root><name>XMLBulk$n</name><price>$($n*2).00</price></root>"
  Invoke-WebRequest -Method POST -Uri "http://127.0.0.1:8000/api/products/" `
    -Headers @{Authorization="Bearer $env:TOKEN";Accept="application/xml"} `
    -ContentType "application/xml" -Body $xml | Out-Null
  if ($n % 5 -eq 0) { Write-Host "> $n produits XML créés" }
}
```

---

## 8) Vérifier dans SQLite

```powershell
sqlite3.exe .\db.sqlite3 "SELECT COUNT(*) FROM products_product;"
sqlite3.exe .\db.sqlite3 "SELECT id, name, price, created_at FROM products_product ORDER BY id DESC LIMIT 15;"
```

---

## 9) Cas d’erreurs à tester (utile pour QA)

```powershell
# Prix invalide (0)
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/api/products/" `
  -Headers @{Authorization="Bearer $env:TOKEN";Accept="application/json"} `
  -ContentType "application/json" `
  -Body (@{name="Bad";price="0"} | ConvertTo-Json) | ConvertTo-Json -Depth 10

# Sans token
Invoke-WebRequest -Method POST -Uri "http://127.0.0.1:8000/api/products/" `
  -ContentType "application/json" -Body '{"name":"NoAuth","price":"9.99"}' -UseBasicParsing

# Content-Type non supporté
Invoke-WebRequest -Method POST -Uri "http://127.0.0.1:8000/api/products/" `
  -Headers @{Authorization="Bearer $env:TOKEN"} `
  -ContentType "text/plain" -Body "name=Weird&price=1.23" -UseBasicParsing
```

---

## 10) Export du schéma OpenAPI

```powershell
python manage.py spectacular --file schema.json   # JSON
python manage.py spectacular --file schema.yaml   # YAML
```

---

## 11) Raccourcis utiles

```powershell
# Top 10 par prix décroissant (JSON)
(Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/products/?ordering=-price" `
  -Headers @{Accept="application/json"}).results |
  Select-Object -First 10 | ConvertTo-Json -Depth 10

# Première page triée par date descendante (XML)
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/products/?ordering=-created_at" `
  -Headers @{Accept="application/xml"} |
  Select-Object -ExpandProperty Content
```

---

### À retenir

* **Windows PowerShell** : utiliser `Invoke-RestMethod` (JSON) ou `Invoke-WebRequest` (XML).
* **JWT** requis pour les requêtes d’écriture (`Authorization: Bearer $env:TOKEN`).
* Toujours préciser **Content-Type** et **Accept**.
* Pas de `make` sous Windows — utiliser les commandes Python directes.
* JSON et XML sont des **formats d’échange**, pas de stockage.
