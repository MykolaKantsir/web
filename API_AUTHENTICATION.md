# Token Authentication API Documentation

## Overview

This Django project now supports **dual authentication**:
1. **Token Authentication** (for Android apps) - No CSRF required
2. **Session Authentication** (for web browsers and Python scripts) - CSRF required as before

Both methods can be used simultaneously without any conflicts.

## API Endpoints

### 1. Login (Obtain Token)

**Endpoint:** `POST /api/auth/login/`

**Request:**
```json
{
    "username": "your_username",
    "password": "your_password"
}
```

**Response (Success - 200 OK):**
```json
{
    "token": "abc123def456...",
    "user_id": 1,
    "username": "your_username",
    "email": "user@example.com"
}
```

**Response (Error - 400 Bad Request):**
```json
{
    "non_field_errors": [
        "Unable to log in with provided credentials."
    ]
}
```

### 2. Logout (Delete Token)

**Endpoint:** `POST /api/auth/logout/`

**Headers:**
```
Authorization: Token abc123def456...
```

**Response (Success - 200 OK):**
```json
{
    "message": "Successfully logged out"
}
```

### 3. Validate Token

**Endpoint:** `GET /api/auth/validate/`

**Headers:**
```
Authorization: Token abc123def456...
```

**Response (Success - 200 OK):**
```json
{
    "valid": true,
    "user_id": 1,
    "username": "your_username",
    "email": "user@example.com"
}
```

## Android App Integration

### Using the Token Authentication

#### Step 1: Login and Get Token

```kotlin
// Example using Retrofit/OkHttp
val loginRequest = LoginRequest(
    username = "user",
    password = "pass"
)

val response = apiService.login(loginRequest)
val token = response.token

// Save token securely (SharedPreferences, Keystore, etc.)
saveToken(token)
```

#### Step 2: Use Token in Subsequent Requests

```kotlin
// Add token to all API requests
val client = OkHttpClient.Builder()
    .addInterceptor { chain ->
        val request = chain.request().newBuilder()
            .addHeader("Authorization", "Token $token")
            .build()
        chain.proceed(request)
    }
    .build()
```

#### Step 3: Access Protected Endpoints

All your existing Django views can now accept token authentication automatically:

- **Inventory endpoints** (`/inventory/...`)
- **Monitoring endpoints** (`/monitoring/...`)
- **Measuring endpoints** (`/measuring/...`)

No changes needed to your existing views - they will accept both token and session authentication!

## Python Scripts (Existing Code)

Your existing Python scripts **don't need any changes**. They will continue to work with cookie-based session authentication and CSRF tokens as before.

Example of existing Python script (no changes needed):
```python
import requests

session = requests.Session()

# Login as before
login_data = {
    'username': 'user',
    'password': 'pass',
    'csrfmiddlewaretoken': csrf_token
}
session.post('https://yoursite.com/accounts/login/', data=login_data)

# Continue using session with CSRF as before
response = session.post('https://yoursite.com/inventory/add/',
                       data=data,
                       headers={'X-CSRFToken': csrf_token})
```

## How Dual Authentication Works

Django REST Framework will check authentication in this order:

1. **First**: Check for `Authorization: Token ...` header
   - If present and valid → authenticate user (no CSRF check)
   - If present but invalid → return 401 Unauthorized

2. **Second**: Check for session cookie
   - If present and valid → authenticate user (CSRF check applies)
   - If present but invalid → return 403 Forbidden

## Security Notes

### For Android App:
- Store tokens securely (Android Keystore recommended)
- Never hardcode tokens in your app
- Implement token refresh mechanism if needed
- Use HTTPS only in production

### For Python Scripts:
- Continue using CSRF protection as before
- Keep credentials secure
- Use environment variables for sensitive data

## Migration Steps (When Deploying)

When deploying to your server with database access, run:

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations to create authtoken table
python manage.py migrate

# The authtoken_token table will be created automatically
```

## Testing the API

### Using curl:

```bash
# Login
curl -X POST https://yoursite.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# Use token
curl https://yoursite.com/monitoring/data/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"

# Logout
curl -X POST https://yoursite.com/api/auth/logout/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### Using Postman:

1. Create a POST request to `/api/auth/login/`
2. Set Body to raw JSON:
   ```json
   {
       "username": "your_username",
       "password": "your_password"
   }
   ```
3. Send request and copy the token from response
4. For other requests, add header: `Authorization: Token YOUR_TOKEN`

## Troubleshooting

### "Authentication credentials were not provided"
- Make sure you're sending the `Authorization: Token ...` header
- Check that the token is correct (no extra spaces)

### "Invalid token"
- The token may have been deleted (user logged out)
- Generate a new token by logging in again

### Python scripts stopped working
- They shouldn't! Double-check that you're still sending CSRF tokens
- Session authentication is still fully supported

## Summary

✅ **Android app**: Use token authentication (no CSRF hassle)
✅ **Python scripts**: Continue using session + CSRF (no changes needed)
✅ **Web browsers**: Continue using session + CSRF (no changes needed)
✅ **All three apps** (Inventory, Monitoring, Measuring): Ready for Android!

The system is backwards compatible - nothing breaks!
