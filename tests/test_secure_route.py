# test_main.py
from fastapi.testclient import TestClient
from main import app
from authentication import create_access_token

client = TestClient(app)

def test_protected_route_with_valid_token():
    # Create a valid token
    token = create_access_token(data={"sub": "shamsundar"})
    
    # Make a request to the protected route with the token in the header
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    
    
    # Assert the response
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, shamsundar"}

def test_protected_route_with_invalid_token():
    # Use an invalid token
    invalid_token = "some.invalid.token"
    
    # Make a request to the protected route with the invalid token
    response = client.get("/protected", headers={"Authorization": f"Bearer {invalid_token}"})
    
    # Assert that access is denied
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}

def test_protected_route_without_token():
    # Make a request to the protected route without any token
    response = client.get("/protected")
    
    # Assert that access is denied
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


if __name__ == "__main__":
    test_protected_route_with_valid_token()
    test_protected_route_with_invalid_token()
    test_protected_route_without_token()
    