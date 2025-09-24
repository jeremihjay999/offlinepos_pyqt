# Chambu POS API Documentation

## Table of Contents
- [Overview](#overview)
- [Base URL](#base-url)
- [Endpoints](#endpoints)
  - [Request Activation](#request-activation)
  - [Verify OTP](#verify-otp)
- [Integration Examples](#integration-examples)
  - [cURL](#curl)
  - [PHP](#php)
  - [Python](#python)
  - [Node.js](#nodejs)
- [Response Codes](#response-codes)
- [Error Handling](#error-handling)

## Overview
This documentation provides information about the Chambu POS API endpoints for OTP-based activation system.

## Base URL
```
https://patanews.co.ke/pos/
```

## Endpoints

### Request Activation
Creates a new activation request.

**Endpoint:** `request_code.php`  
**Method:** `POST`  
**Content-Type:** `application/json`

#### Request Body
```json
{
    "phone": "254712345678",
    "name": "John Doe"
}
```

#### cURL Example

**Linux/macOS (bash/zsh):**
```bash
curl -X POST https://patanews.co.ke/pos/request_code.php \
  -H "Content-Type: application/json" \
  -d '{"phone": "254712345678", "name": "John Doe"}'
```

**Windows (cmd.exe):**
```shell
curl -X POST https://patanews.co.ke/pos/request_code.php -H "Content-Type: application/json" -d "{\"phone\": \"254712345678\", \"name\": \"John Doe\"}"
```

#### Success Response (201 Created)
```json
{
    "success": true,
    "message": "Request saved"
}
```

### Verify OTP
Verifies an OTP for activation.

**Endpoint:** `verify_code.php`  
**Method:** `POST`  
**Content-Type:** `application/json`

#### Request Body
```json
{
    "phone": "254712345678",
    "otp": "123456"
}
```

#### cURL Example

**Linux/macOS (bash/zsh):**
```bash
curl -X POST https://patanews.co.ke/pos/verify_code.php \
  -H "Content-Type: application/json" \
  -d '{"phone": "254712345678", "otp": "123456"}'
```

**Windows (cmd.exe):**
```shell
curl -X POST https://patanews.co.ke/pos/verify_code.php -H "Content-Type: application/json" -d "{\"phone\": \"254712345678\", \"otp\": \"123456\"}"
```

#### Success Response (200 OK)
```json
{
    "success": true,
    "message": "Activation successful."
}
```

## Integration Examples

### cURL
Note: The `curl` command syntax for sending JSON data differs between Linux/macOS and Windows `cmd.exe` due to differences in how they handle quotes.

#### Request Activation

**Linux/macOS (bash/zsh):**
```bash
curl -X POST https://patanews.co.ke/pos/request_code.php \
  -H "Content-Type: application/json" \
  -d '{"phone": "254712345678", "name": "John Doe"}'
```

**Windows (cmd.exe):**
```shell
curl -X POST https://patanews.co.ke/pos/request_code.php -H "Content-Type: application/json" -d "{\"phone\": \"254712345678\", \"name\": \"John Doe\"}"
```

#### Verify OTP

**Linux/macOS (bash/zsh):**
```bash
curl -X POST https://patanews.co.ke/pos/verify_code.php \
  -H "Content-Type: application/json" \
  -d '{"phone": "254712345678", "otp": "123456"}'
```

**Windows (cmd.exe):**
```shell
curl -X POST https://patanews.co.ke/pos/verify_code.php -H "Content-Type: application/json" -d "{\"phone\": \"254712345678\", \"otp\": \"123456\"}"
```

### PHP
```php
<?php
// Request activation
$data = ["phone" => "254712345678", "name" => "John Doe"];
$ch = curl_init('https://patanews.co.ke/pos/request_code.php');
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_POST => true,
    CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
    CURLOPT_POSTFIELDS => json_encode($data)
]);
$response = curl_exec($ch);
echo $response;

// Verify OTP
$data = ["phone" => "254712345678", "otp" => "123456"];
$ch = curl_init('https://patanews.co.ke/pos/verify_code.php');
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_POST => true,
    CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
    CURLOPT_POSTFIELDS => json_encode($data)
]);
$response = curl_exec($ch);
echo $response;
?>
```

### Python
```python
import requests

# Request activation
response = requests.post(
    'https://patanews.co.ke/pos/request_code.php',
    json={'phone': '254712345678', 'name': 'John Doe'}
)
print(response.json())

# Verify OTP
response = requests.post(
    'https://patanews.co.ke/pos/verify_code.php',
    json={'phone': '254712345678', 'otp': '123456'}
)
print(response.json())
```

### Node.js
```javascript
const axios = require('axios');

// Request activation
async function requestActivation() {
    try {
        const response = await axios.post('https://patanews.co.ke/pos/request_code.php', {
            phone: '254712345678',
            name: 'John Doe'
        });
        console.log(response.data);
    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
    }
}

// Verify OTP (after user enters the OTP)
async function verifyOTP() {
    try {
        const response = await axios.post('https://patanews.co.ke/pos/verify_code.php', {
            phone: '254712345678',
            otp: '123456'  // The OTP sent to the user
        });
        console.log(response.data);
    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
    }
}

// Call the functions
requestOTP();
// verifyOTP();  // Uncomment to verify OTP
```

## Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Missing or invalid parameters |
| 500 | Internal Server Error |

## Error Handling
All error responses will include a JSON object with a `success` field set to `false` and a `message` field describing the error.

Example error response:
```json
{
    "success": false,
    "message": "Phone and OTP are required."
}
```

## Notes
- The `name` field is stored in the database for reference but is not used for authentication.
- OTPs are valid for a limited time (implementation dependent on your server configuration).
- The system allows multiple requests for the same phone number as long as there are no pending requests.