# Performance Configuration Guide

## Bcrypt Configuration for Different Environments

### Development/Testing (Current Configuration)
- **BCRYPT_ROUNDS=4** (16 iterations, ~10ms per hash)
- **Use Case**: Fast development, testing, CI/CD pipelines
- **Security**: Adequate for development environments
- **Performance**: Optimized for speed (~50ms login time)

### Production (Recommended Configuration)  
- **BCRYPT_ROUNDS=12** (4096 iterations, ~300ms per hash)
- **Use Case**: Production environments with real user data
- **Security**: Industry standard, highly secure against brute force
- **Performance**: Acceptable for production (~350ms login time)

### High-Security Environments
- **BCRYPT_ROUNDS=15** (32768 iterations, ~2.5s per hash)
- **Use Case**: High-security applications (banking, healthcare)
- **Security**: Maximum protection against advanced attacks
- **Performance**: Slower but acceptable for high-security needs

## Performance Impact Analysis

| Rounds | Iterations | Time/Hash | Login Time | Security Level |
|--------|------------|-----------|------------|----------------|
| 4      | 16         | ~10ms     | ~50ms      | Development    |
| 10     | 1024       | ~100ms    | ~150ms     | Light Prod     |
| 12     | 4096       | ~300ms    | ~350ms     | Standard Prod  |
| 15     | 32768      | ~2.5s     | ~2.6s      | High Security  |

## Configuration Management

### Environment Variables
```bash
# Development
BCRYPT_ROUNDS=4

# Production  
BCRYPT_ROUNDS=12

# High Security
BCRYPT_ROUNDS=15
```

### Auto-Scaling Considerations
- Lower bcrypt rounds for auto-scaling environments
- Monitor CPU usage during authentication peaks
- Consider Redis-based session management for scale

### Migration Strategy
When changing bcrypt rounds:
1. Users with old hashes will still work (backward compatible)
2. New password hashes will use the new rounds setting
3. Optional: Force password reset for all users to update hashes
4. Gradual migration: Update hashes during normal login flow

## Performance Monitoring
- Monitor login response times in production
- Set up alerts for login times > 500ms
- Track authentication success/failure rates
- Monitor CPU usage during peak authentication times

## Security vs Performance Balance
- **Development**: Prioritize speed (rounds=4)
- **Staging**: Match production settings (rounds=12) 
- **Production**: Balance security and UX (rounds=12)
- **High Security**: Prioritize security over speed (rounds=15)