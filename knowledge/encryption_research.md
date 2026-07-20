# Encryption Research for ShadowC2

## AES-256-CBC
- Symmetric encryption
- Key must be 32 bytes (256 bits)
- IV (Initialization Vector) must be random and 16 bytes
- Store key in `.env` file

## JWT (JSON Web Tokens)
- For authenticating dashboard users
- Token contains user ID and expiration
- Signature ensures token integrity

## Implementation Plan
1. Add `cryptography` or `pycryptodome` to backend
2. Encrypt all C2 traffic (commands + results)
3. Store encryption keys in `.env` (never commit)
4. Decrypt on server before processing

## Stealth Consideration
- Encrypted traffic looks like random bytes
- Use base64 encoding for transport (to make it look like normal text)