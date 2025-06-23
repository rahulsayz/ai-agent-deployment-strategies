import asyncio
import time
from collections import deque
from typing import Dict, List

class RequestBasedScaler:
    def __init__(self, target_queue_size: int = 10, scale_cooldown: int = 300):
        self.target_queue_size = target_queue_size
        self.scale_cooldown = scale_cooldown
        self.last_scale_time = 0
        self.request_queue = asyncio.Queue()
        self.response_times = deque(maxlen=100)
        
    async def monitor_and_scale(self):
        """Monitor queue depth and response times for scaling decisions."""
        while True:
            current_time = time.time()
            queue_size = self.request_queue.qsize()
            avg_response_time = self.get_average_response_time()
            
            should_scale_up = (
                queue_size > self.target_queue_size or
                avg_response_time > 5.0  # 5 second threshold
            ) and (current_time - self.last_scale_time) > self.scale_cooldown
            
            should_scale_down = (
                queue_size < self.target_queue_size // 2 and
                avg_response_time < 2.0  # 2 second threshold
            ) and (current_time - self.last_scale_time) > self.scale_cooldown
            
            if should_scale_up:
                await self.scale_up()
                self.last_scale_time = current_time
            elif should_scale_down:
                await self.scale_down()
                self.last_scale_time = current_time
            
            await asyncio.sleep(30)  # Check every 30 seconds
    
    def get_average_response_time(self) -> float:
        """Calculate average response time from recent requests."""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)
    
    async def scale_up(self):
        """Trigger scale-up operations."""
        print("Scaling up AI agent instances...")
        # Implement your scaling logic here
        # - Add new pods in Kubernetes
        # - Launch new EC2 instances
        # - Add containers to ECS service
        
    async def scale_down(self):
        """Trigger scale-down operations."""
        print("Scaling down AI agent instances...")
        # Implement graceful scale-down logic here