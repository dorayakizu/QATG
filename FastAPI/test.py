import requests

response = requests.get(
    "http://localhost:8069/web/database/list",
    headers={
        "X-API-Key": "my-secret-key"
    }
)

print(response.json())