# InvivoDB Security Configuration

## Admin Authentication

The application includes a secure admin authentication system to protect administrative functions.

### Environment Variables (Required for Production)

**For Production Deployment:**

1. **ADMIN_PASSWORD_HASH** - SHA256 hash of the admin password
   ```bash
   # Generate the hash (replace 'your_secure_password' with actual password)
   echo -n "your_secure_password" | sha256sum
   
   # Set in production environment
   export ADMIN_PASSWORD_HASH=your_sha256_hash_here
   ```

2. **SECRET_KEY** - Flask session secret key (required)
   ```bash
   # Generate a secure secret key
   python -c "import secrets; print(secrets.token_hex(32))"
   
   # Set in production environment
   export SECRET_KEY=your_generated_secret_key_here
   ```

### Development Environment

**For Development Only:**
```bash
# Simple password authentication (NOT for production)
export ADMIN_PASSWORD=your_dev_password_here
export FLASK_ENV=development
```

### Password Hash Generation

To generate a password hash for production:

```bash
# Method 1: Using Python
python3 -c "import hashlib; print(hashlib.sha256('your_password_here'.encode()).hexdigest())"

# Method 2: Using command line
echo -n "your_password_here" | sha256sum | cut -d' ' -f1
```

### Security Features

1. **Session-based Authentication**: Admin sessions are managed securely
2. **Password Hashing**: Production uses SHA256 hashing (never stores plain text)
3. **Environment Variables**: No secrets stored in code
4. **Route Protection**: Admin routes require authentication
5. **Session Timeout**: Sessions expire when browser closes
6. **Access Logging**: Failed login attempts are logged

### Protected Routes

- `/admin/login` - Admin login page (public)
- `/admin/logout` - Admin logout (clears session)
- `/admin/species` - Species management (protected)
- `/admin/species/<id>/edit` - Edit species descriptions (protected)

### Security Best Practices

1. **Never commit passwords or hashes to version control**
2. **Use strong passwords (12+ characters, mixed case, numbers, symbols)**
3. **Rotate admin passwords regularly**
4. **Monitor admin access logs**
5. **Use HTTPS in production**
6. **Set secure environment variables in deployment platform**

### Deployment Platform Configuration

**Render.com:**  (used here)
```bash
# Set environment variables in Render dashboard
ADMIN_PASSWORD_HASH=your_sha256_hash
SECRET_KEY=your_secret_key
FLASK_ENV=production
```

**Heroku:**
```bash
heroku config:set ADMIN_PASSWORD_HASH=your_sha256_hash
heroku config:set SECRET_KEY=your_secret_key
heroku config:set FLASK_ENV=production
```

### Security Incident Response

If admin credentials are compromised:

1. Immediately change the admin password
2. Generate new password hash
3. Update environment variables
4. Redeploy the application
5. Review access logs for unauthorized activity

### Audit Trail

- Failed login attempts are logged with flash messages
- Successful logins redirect to admin interface
- All admin actions should be logged (future enhancement)

---

**Important**: This authentication system provides basic security for a research database. For production environments with sensitive data, consider implementing:

- Multi-factor authentication
- Role-based access control
- Database connection encryption
- Regular security audits
- Intrusion detection systems