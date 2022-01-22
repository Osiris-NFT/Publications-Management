import requests

def test_if_service_alive():
    response = requests.get("http://0.0.0.0:8000/")
    assert response.status_code == 200
