
import unittest
from datetime import timedelta, datetime, timezone
from authentication import create_access_token, verify_token
import jwt

class TestJWTTokenFunctions(unittest.TestCase):

    def setUp(self):
        # Setup sample payload and secret for testing
        self.sample_payload = {"sub": "testuser"}
        self.invalid_token = "invalid.token.string"

    def test_create_access_token(self):
        # Test creating a token with default expiration
        token = create_access_token(self.sample_payload)
        self.assertIsInstance(token, str, "Token should be a string")
        
        # Decode the token to ensure it contains expected data
        decoded_token = verify_token(token)
        self.assertEqual(decoded_token["sub"], self.sample_payload["sub"], "Token payload should match input payload")
        
    def test_create_access_token_with_custom_expiration(self):
        # Test creating a token with custom expiration
        custom_expiration = timedelta(minutes=2)
        token = create_access_token(self.sample_payload, expires_delta=custom_expiration)
        decoded_token = verify_token(token)
        
        # Check if the token has a short expiration
        expiration_time = decoded_token["exp"]
        self.assertAlmostEqual(expiration_time, (datetime.now(timezone.utc) + custom_expiration).timestamp(), delta=5, msg="Token expiration should match custom expiration")

    def test_verify_token(self):
        # Test verifying a valid token
        token = create_access_token(self.sample_payload)
        decoded_payload = verify_token(token)
        
        self.assertIsNotNone(decoded_payload, "Decoded payload should not be None for a valid token")
        self.assertEqual(decoded_payload["sub"], self.sample_payload["sub"], "Decoded payload should match the original payload")

    def test_verify_expired_token(self):
        # Create a token with immediate expiration to test expired token scenario
        token = create_access_token(self.sample_payload, expires_delta=timedelta(seconds=0))
        
        # Verify the token immediately, should be expired
        decoded_payload = verify_token(token)
        self.assertIsNone(decoded_payload, "Decoded payload should be None for an expired token")

    def test_verify_invalid_token(self):
        # Test verifying an invalid token
        decoded_payload = verify_token(self.invalid_token)
        self.assertIsNone(decoded_payload, "Decoded payload should be None for an invalid token")

if __name__ == "__main__":
    unittest.main()
