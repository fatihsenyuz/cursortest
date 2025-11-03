"""
Rate Limiting Module
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
import os

# Initialize limiter
if os.environ.get('RATE_LIMIT_ENABLED', 'true').lower() == 'true':
    limiter = Limiter(key_func=get_remote_address)
else:
    # Create a dummy limiter when rate limiting is disabled
    class DummyLimiter:
        def limit(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
    
    limiter = DummyLimiter()

# Rate limit configuration
RATE_LIMIT_ENABLED = os.environ.get('RATE_LIMIT_ENABLED', 'true').lower() == 'true'

# Rate limit decorator
def rate_limit(times: str = "10/minute", per_method: bool = True):
    """
    Rate limit decorator
    
    Args:
        times: Rate limit string (e.g., "10/minute", "100/hour")
        per_method: Whether to limit per HTTP method
    """
    if not RATE_LIMIT_ENABLED:
        # Return a no-op decorator
        def noop_decorator(func):
            return func
        return noop_decorator
    
    return limiter.limit(times)

# Common rate limit configurations
LIMITS = {
    'login': "5/minute",           # Login attempts
    'register': "3/hour",          # Registration
    'api': "100/minute",           # General API calls
    'stats': "20/minute",          # Stats endpoints
    'sms': "100/hour",             # SMS sending
}

