# API Response Standard

All API responses follow a consistent pattern for better client integration.

## Standard Response Format

```json
{
  "status_code": 200,
  "success": true|false,
  "message": "Human-readable message",
  "data": { ... },           // Response data (present on success)
  "metadata": { ... },       // Optional (pagination info, etc.)
  "errors": [ ... ]          // Optional (validation errors, etc.)
}
```

## Success Response Example

```json
{
  "status_code": 200,
  "success": true,
  "message": "Resource retrieved successfully",
  "data": {
    "id": "123",
    "name": "EcoRoute Atlas"
  }
}
```

## Error Response Example

```json
{
  "status_code": 404,
  "success": false,
  "message": "Resource not found",
  "data": null,
  "errors": null
}
```

## Validation Error Example

```json
{
  "status_code": 422,
  "success": false,
  "message": "Validation error",
  "data": null,
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format",
      "type": "value_error.email"
    }
  ]
}
```

## Paginated Response Example

```json
{
  "status_code": 200,
  "success": true,
  "message": "Items retrieved successfully",
  "data": [
    { "id": "1", "name": "Item 1" },
    { "id": "2", "name": "Item 2" }
  ],
  "metadata": {
    "total": 100,
    "page": 1,
    "page_size": 10,
    "has_next": true,
    "has_prev": false
  }
}
```

## HTTP Status Codes

- `200` - Success
- `201` - Created
- `204` - No Content
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

## Using ResponseBuilder Helper

Instead of hardcoding responses, use the `ResponseBuilder` class:

```python
from app.core.response import ResponseBuilder
from fastapi import status

# Success response
return ResponseBuilder.success(
    data=user_data,
    message="User retrieved successfully"
)

# Created response (201)
return ResponseBuilder.created(
    data=new_user,
    message="User created successfully"
)

# Not found error
return ResponseBuilder.not_found(
    message="User not found"
)

# Validation error
return ResponseBuilder.validation_error(
    errors=validation_errors,
    message="Invalid input data"
)

# Paginated response
return ResponseBuilder.paginated(
    data=users_list,
    total=100,
    page=1,
    page_size=10,
    message="Users retrieved successfully"
)
```

### Available Helper Methods

- `ResponseBuilder.success()` - 200 OK
- `ResponseBuilder.created()` - 201 Created
- `ResponseBuilder.no_content()` - 204 No Content
- `ResponseBuilder.bad_request()` - 400 Bad Request
- `ResponseBuilder.unauthorized()` - 401 Unauthorized
- `ResponseBuilder.forbidden()` - 403 Forbidden
- `ResponseBuilder.not_found()` - 404 Not Found
- `ResponseBuilder.validation_error()` - 422 Validation Error
- `ResponseBuilder.error()` - Generic error with custom status code
- `ResponseBuilder.paginated()` - Paginated list response
