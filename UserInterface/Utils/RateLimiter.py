import time
from threading import Lock

class RateLimiter:
    def __init__(self, max_requests=60, window_size=60):
        self.max_requests = max_requests
        self.window_size = window_size
        self.requests = []
        self.lock = Lock()

    def wait_if_needed(self):
        with self.lock:
            current_time = time.time()
            
            # Remove old requests outside the window
            self.requests = [req_time for req_time in self.requests 
                           if current_time - req_time <= self.window_size]
            
            # If we've hit the limit, wait until oldest request expires
            if len(self.requests) >= self.max_requests:
                sleep_time = self.requests[0] + self.window_size - current_time
                if sleep_time > 0:
                    time.sleep(sleep_time)
                self.requests = self.requests[1:]
            
            # Add current request
            self.requests.append(current_time)
