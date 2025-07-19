#!/bin/bash

echo "Creating .env file..."
cat > .env << 'EOL'
# Database Configuration
# Replace with your actual Supabase database URL
# Format: postgresql://username:password@host:port/database
SUPABASE_DB_URL=postgresql://postgres:your_password@db.your_project.supabase.co:5432/postgres

# JWT Configuration
# Generate a secure secret key for JWT tokens
SECRET_KEY=your-secret-key-here-change-in-production

# Environment
ENVIRONMENT=development
EOL

echo ".env file created successfully!"
echo "Please edit the .env file with your actual Supabase credentials."
echo "Run: nano .env"
