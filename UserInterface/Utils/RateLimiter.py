import time
from collections import deque
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests=60, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window  # in seconds
        self.requests = deque()
    
    def wait_if_needed(self):
        now = datetime.now()
        
        # Remove old requests
        while self.requests and self.requests[0] < now - timedelta(seconds=self.time_window):
            self.requests.popleft()
        
        # If at capacity, wait until oldest request expires
        if len(self.requests) >= self.max_requests:
            wait_time = (self.requests[0] + timedelta(seconds=self.time_window) - now).total_seconds()
            if wait_time > 0:
                time.sleep(wait_time)
        
        # Add current request
        self.requests.append(now)
