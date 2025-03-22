from nyx_security import TokenManager, encrypt_data, decrypt_data

# Create a token manager
manager = TokenManager()

# Split and store a token
original_token = "your-super-secret-api-token-here"
token_parts = manager.store_token("my_api_token", original_token)

print("Token parts:")
for part in token_parts:
    print(f"  {part}")

# List stored tokens
print("\nStored tokens:")
for token_name in manager.list_tokens():
    print(f"  {token_name}")

# Retrieve the original token
retrieved_token = manager.retrieve_token("my_api_token")
print("\nRetrieved token:")
print(retrieved_token)

# Verify it matches the original
print("\nMatches original:", retrieved_token == original_token)

# Example of encryption and decryption
sensitive_data = "This is sensitive information that needs to be protected"
password = "secure-password-123"

# Encrypt the data
encrypted = encrypt_data(sensitive_data, password)
print("\nEncrypted data:")
for key, value in encrypted.items():
    print(f"  {key}: {value}")

# Decrypt the data
decrypted = decrypt_data(
    encrypted["encrypted_data"], 
    password, 
    encrypted["salt"], 
    encrypted["iv"], 
    encrypted["mac"]
)
print("\nDecrypted data:")
print(decrypted)