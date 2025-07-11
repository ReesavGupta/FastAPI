import time
from fastapi import Request, HTTPException, status
from typing import Dict, Tuple

class RateLimiter:
    def __init__(self, limit: int, period: int):
        self.limit = limit
        self.period = period  # seconds
        self.access_records: Dict[Tuple[str, str], list] = {}

    def check(self, ip: str, endpoint: str):
        now = time.time()
        key = (ip, endpoint)
        records = self.access_records.get(key, [])
        # Remove records outside the period
        records = [t for t in records if now - t < self.period]
        if len(records) >= self.limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        records.append(now)
        self.access_records[key] = records

# In-memory token blacklist for logout
blacklisted_tokens = set()

def blacklist_token(token: str):
    blacklisted_tokens.add(token)

def is_token_blacklisted(token: str) -> bool:
    return token in blacklisted_tokens

forgot_password_limiter = RateLimiter(1, 60)  # 1 request per 60 seconds per IP

login_limiter = RateLimiter(5, 60)  # 5 requests per 60 seconds per IP
register_limiter = RateLimiter(3, 60)  # 3 requests per 60 seconds per IP
general_api_limiter = RateLimiter(100, 60)  # 100 requests per 60 seconds per IP

# Example usage:
# limiter = RateLimiter(5, 60)  # 5 requests per 60 seconds
# limiter.check(ip, endpoint) 