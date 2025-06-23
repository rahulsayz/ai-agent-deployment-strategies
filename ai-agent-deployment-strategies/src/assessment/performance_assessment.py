import time
import asyncio
import statistics
from typing import List, Dict
import psutil
import GPUtil

class ProductionReadinessAssessment:
    def __init__(self, agent_instance):
        self.agent = agent_instance
        self.metrics = {
            'response_times': [],
            'memory_usage': [],
            'gpu_utilization': [],
            'cpu_usage': []
        }
    
    async def run_load_test(self, concurrent_users: int = 100, 
                           duration_minutes: int = 10) -> Dict:
        """Simulate production load to assess agent performance."""
        test_queries = [
            "What are the latest trends in artificial intelligence?",
            "Help me analyze this data and provide insights.",
            "Can you summarize the key points from our conversation?",
            "What recommendations do you have for improving efficiency?"
        ]
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        async def simulate_user():
            while time.time() < end_time:
                query = random.choice(test_queries)
                start = time.time()
                
                try:
                    response = await self.agent.process_query(query)
                    response_time = time.time() - start
                    self.metrics['response_times'].append(response_time)
                    
                    # Collect system metrics
                    self.metrics['memory_usage'].append(psutil.virtual_memory().percent)
                    self.metrics['cpu_usage'].append(psutil.cpu_percent())
                    
                    if GPUtil.getGPUs():
                        gpu = GPUtil.getGPUs()[0]
                        self.metrics['gpu_utilization'].append(gpu.load * 100)
                
                except Exception as e:
                    print(f"Error during load test: {e}")
                
                await asyncio.sleep(1)  # 1 second between requests per user
        
        # Run concurrent user simulations
        tasks = [simulate_user() for _ in range(concurrent_users)]
        await asyncio.gather(*tasks)
        
        return self.generate_report()
    
    def generate_report(self) -> Dict:
        """Generate performance assessment report."""
        return {
            'response_time_stats': {
                'mean': statistics.mean(self.metrics['response_times']),
                'median': statistics.median(self.metrics['response_times']),
                'p95': statistics.quantiles(self.metrics['response_times'], n=20)[18],
                'p99': statistics.quantiles(self.metrics['response_times'], n=100)[98]
            },
            'resource_utilization': {
                'avg_memory': statistics.mean(self.metrics['memory_usage']),
                'peak_memory': max(self.metrics['memory_usage']),
                'avg_cpu': statistics.mean(self.metrics['cpu_usage']),
                'avg_gpu': statistics.mean(self.metrics['gpu_utilization']) if self.metrics['gpu_utilization'] else 0
            },
            'recommendations': self.get_deployment_recommendations()
        }
    
    def get_deployment_recommendations(self) -> List[str]:
        """Provide deployment recommendations based on assessment."""
        recommendations = []
        
        avg_response_time = statistics.mean(self.metrics['response_times'])
        if avg_response_time > 2.0:
            recommendations.append("Consider GPU acceleration or model optimization")
        
        peak_memory = max(self.metrics['memory_usage'])
        if peak_memory > 80:
            recommendations.append("Increase memory allocation or implement model quantization")
        
        if statistics.mean(self.metrics['gpu_utilization']) < 50:
            recommendations.append("Optimize GPU utilization or consider smaller GPU instances")
        
        return recommendations