# Admin User Configuration

This personal blog platform supports configurable admin user credentials through environment variables.

## Environment Variables

Set these variables in your `.env` file to customize the admin user:

```bash
# Admin User Configuration
ADMIN_EMAIL=your-admin@example.com        # Admin user email
ADMIN_PASSWORD=YourSecurePassword123!     # Admin user password  
ADMIN_USERNAME=admin                      # Admin username
ADMIN_FULL_NAME=Your Full Name            # Admin display name
```

## Default Values

If not specified, the following defaults are used:

- **ADMIN_EMAIL**: `admin@example.com`
- **ADMIN_PASSWORD**: `AdminP@ss_w0rd!`
- **ADMIN_USERNAME**: `admin`
- **ADMIN_FULL_NAME**: `Admin User`

## Usage

### 1. Configure Admin Credentials

Edit your `.env` file:

```bash
# Copy from .env.example
cp .env.example .env

# Edit with your credentials
nano .env
```

### 2. Start the Application

```bash
# Start containers - admin user will be created automatically
docker compose up -d
```

### 3. Verify Admin User Creation

```bash
# Check if admin user was created successfully
docker compose exec backend python create_test_data.py
```

### 4. Access Admin Dashboard

- Login at: http://localhost:3000/login
- Use your configured `ADMIN_EMAIL` and `ADMIN_PASSWORD`
- Access admin dashboard at: http://localhost:3000/admin

## Security Notes

- **Change default credentials** before deploying to production
- Use **strong passwords** with mixed case, numbers, and symbols
- Keep your `.env` file **secure** and never commit it to version control
- The `.env.example` file shows the format without exposing real credentials

## Testing Different Configurations

You can test different admin configurations by:

1. Stopping containers: `docker compose down`
2. Updating `.env` file with new credentials
3. Removing existing admin user: `docker compose exec backend python -c "from src.database import SessionLocal; from src.models.user import User; db=SessionLocal(); db.query(User).filter(User.email=='old-admin@example.com').delete(); db.commit()"`
4. Starting containers: `docker compose up -d`
5. The new admin user will be created with updated credentials