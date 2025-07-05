# Third Wheel Backend Setup Guide

## Database Configuration

### 1. Install Dependencies
```bash
cd tw-backend
make install
```

### 2. Environment Variables
Create a `.env` file in the `tw-backend` directory with the following configuration:

```env
# Database Configuration
# Replace with your actual Supabase database URL
# Format: postgresql://username:password@host:port/database
SUPABASE_DB_URL=postgresql://postgres:your_password@db.your_project.supabase.co:5432/postgres

# JWT Configuration
# Generate a secure secret key for JWT tokens
SECRET_KEY=your-secret-key-here-change-in-production

# Environment
ENVIRONMENT=development
```

### 3. Get Your Supabase Database URL

1. Go to your Supabase project dashboard
2. Navigate to Settings → Database
3. Find the connection string under "Connection pooling" or "Connection info"
4. The URL format should be: `postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres`

### 4. Generate a Secret Key

You can generate a secure secret key using Python:

```python
import secrets
print(secrets.token_urlsafe(32))
```

### 5. Run the Application

```bash
# Start the development server
make dev

# Or manually:
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user info
- `POST /auth/logout` - Logout user

### Users
- `GET /users/` - Get all users (paginated)
- `GET /users/{user_id}` - Get user by ID
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user (soft delete)
- `GET /users/search/by-username/{username}` - Find user by username
- `GET /users/search/by-email/{email}` - Find user by email
- `POST /users/{user_id}/partner/{partner_id}` - Link users as partners
- `DELETE /users/{user_id}/partner` - Unlink partner

### Health Check
- `GET /health` - API health check
- `GET /` - Welcome message

## Database Models

### User Model
- **id**: Primary key
- **email**: Unique email address
- **username**: Unique username
- **first_name**: User's first name
- **last_name**: User's last name
- **password_hash**: Hashed password
- **is_active**: Account status
- **is_verified**: Email verification status
- **phone_number**: Optional phone number
- **date_of_birth**: Optional date of birth
- **gender**: Optional gender
- **partner_id**: ID of linked partner
- **relationship_status**: Current relationship status
- **created_at**: Account creation timestamp
- **updated_at**: Last update timestamp
- **last_login**: Last login timestamp

### Couple Model
- **id**: Primary key
- **user1_id**: First user ID
- **user2_id**: Second user ID
- **relationship_start_date**: Optional relationship start date
- **is_active**: Relationship status
- **created_at**: Creation timestamp
- **updated_at**: Last update timestamp

## Testing the API

You can test the API using curl, Postman, or any HTTP client:

### Register a new user:
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User",
    "password": "testpassword123"
  }'
```

### Login:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

## Next Steps

1. Set up your Supabase database
2. Configure your `.env` file
3. Install dependencies with `make install`
4. Run the application with `make dev`
5. Test the API endpoints
6. Access the automatic API documentation at `http://localhost:8000/docs` 