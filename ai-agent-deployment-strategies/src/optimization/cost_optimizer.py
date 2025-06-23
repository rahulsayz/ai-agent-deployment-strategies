import asyncio
import time
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class ResourceProfile:
    name: str
    cpu_cores: float
    memory_gb: float
    gpu_count: int
    hourly_cost: float
    max_concurrent_users: int

class CostOptimizer:
    def __init__(self):
        self.resource_profiles = [
            ResourceProfile("nano", 0.5, 1, 0, 0.05, 10),
            ResourceProfile("micro", 1, 2, 0, 0.10, 25),
            ResourceProfile("small", 2, 4, 0, 0.20, 50),
            ResourceProfile("medium", 4, 8, 1, 0.80, 100),
            ResourceProfile("large", 8, 16, 2, 1.60, 200),
            ResourceProfile("xlarge", 16, 32, 4, 3.20, 400)
        ]
        
        self.current_profile = self.resource_profiles[2]  # Start with small
        self.usage_history = []
        self.cost_metrics = {}
    
    async def monitor_usage_and_optimize(self):
        """Continuously monitor usage and optimize costs."""
        while True:
            try:
                current_metrics = await self.collect_usage_metrics()
                optimal_profile = self.calculate_optimal_profile(current_metrics)
                
                if optimal_profile != self.current_profile:
                    await self.transition_to_profile(optimal_profile)
                
                # Update cost tracking
                await self.update_cost_metrics(current_metrics)
                
            except Exception as e:
                print(f"Cost optimization error: {e}")
            
            await asyncio.sleep(300)  # Check every 5 minutes
    
    async def collect_usage_metrics(self) -> Dict:
        """Collect current usage metrics."""
        return {
            'active_users': 75,  # Current active users
            'cpu_utilization': 0.65,  # 65% CPU usage
            'memory_utilization': 0.70,  # 70% memory usage
            'gpu_utilization': 0.80,  # 80% GPU usage
            'requests_per_minute': 120,
            'average_response_time': 1.5,
            'timestamp': time.time()
        }
    
    def calculate_optimal_profile(self, metrics: Dict) -> ResourceProfile:
        """Calculate the most cost-effective resource profile."""
        
        # Determine required capacity based on current load
        required_capacity = max(
            metrics['active_users'],
            metrics['requests_per_minute'] * 0.8  # 80% safety margin
        )
        
        # Find profiles that can handle the load
        suitable_profiles = [
            profile for profile in self.resource_profiles
            if profile.max_concurrent_users >= required_capacity
        ]
        
        if not suitable_profiles:
            # If no single profile is sufficient, use the largest
            return self.resource_profiles[-1]
        
        # Among suitable profiles, consider utilization efficiency
        current_utilization = max(
            metrics['cpu_utilization'],
            metrics['memory_utilization'],
            metrics.get('gpu_utilization', 0)
        )
        
        # Prefer profiles with 60-80% utilization for efficiency
        target_utilization = 0.70
        
        best_profile = min(suitable_profiles, key=lambda p: (
            p.hourly_cost + 
            abs(current_utilization - target_utilization) * 10  # Penalty for poor utilization
        ))
        
        return best_profile
    
    async def transition_to_profile(self, new_profile: ResourceProfile):
        """Transition to a new resource profile."""
        old_profile = self.current_profile
        
        print(f"Transitioning from {old_profile.name} to {new_profile.name}")
        
        # Implement gradual transition to minimize service disruption
        if new_profile.hourly_cost > old_profile.hourly_cost:
            # Scaling up: Add resources first, then remove old ones
            await self.scale_up_to_profile(new_profile)
            await asyncio.sleep(60)  # Wait for new resources to be ready
            await self.scale_down_from_profile(old_profile)
        else:
            # Scaling down: Drain connections first, then remove resources
            await self.drain_connections()
            await self.scale_down_from_profile(old_profile)
            await self.scale_up_to_profile(new_profile)
        
        self.current_profile = new_profile
        
        # Log cost impact
        hourly_savings = old_profile.hourly_cost - new_profile.hourly_cost
        print(f"Hourly cost change: ${hourly_savings:.2f} ({'saved' if hourly_savings > 0 else 'added'})")
    
    async def scale_up_to_profile(self, profile: ResourceProfile):
        """Scale up resources to match profile."""
        # Implement scaling logic (Kubernetes, cloud auto-scaling, etc.)
        print(f"Scaling up to {profile.name}: {profile.cpu_cores} CPU, {profile.memory_gb}GB RAM, {profile.gpu_count} GPU")
    
    async def scale_down_from_profile(self, profile: ResourceProfile):
        """Scale down resources from profile."""
        print(f"Scaling down from {profile.name}")
    
    async def drain_connections(self):
        """Gracefully drain existing connections before scaling down."""
        print("Draining connections...")
        await asyncio.sleep(30)  # Allow time for connections to drain
    
    async def update_cost_metrics(self, usage_metrics: Dict):
        """Update cost tracking metrics."""
        hourly_cost = self.current_profile.hourly_cost
        current_hour = int(time.time() // 3600)
        
        if current_hour not in self.cost_metrics:
            self.cost_metrics[current_hour] = {
                'cost': 0,
                'requests': 0,
                'active_users': 0,
                'profile_used': self.current_profile.name
            }
        
        # Accumulate costs (assuming metrics are collected every 5 minutes)
        self.cost_metrics[current_hour]['cost'] += hourly_cost / 12  # 5min = 1/12 hour
        self.cost_metrics[current_hour]['requests'] += usage_metrics['requests_per_minute'] * 5
        self.cost_metrics[current_hour]['active_users'] = max(
            self.cost_metrics[current_hour]['active_users'],
            usage_metrics['active_users']
        )
    
    def generate_cost_report(self, hours: int = 24) -> Dict:
        """Generate cost analysis report."""
        recent_hours = sorted(self.cost_metrics.keys())[-hours:]
        
        total_cost = sum(self.cost_metrics[hour]['cost'] for hour in recent_hours)
        total_requests = sum(self.cost_metrics[hour]['requests'] for hour in recent_hours)
        avg_cost_per_request = total_cost / max(total_requests, 1)
        
        return {
            'period_hours': hours,
            'total_cost': total_cost,
            'total_requests': total_requests,
            'cost_per_request': avg_cost_per_request,
            'cost_breakdown': {
                hour: self.cost_metrics[hour] for hour in recent_hours
            },
            'recommendations': self.get_cost_optimization_recommendations()
        }
    
    def get_cost_optimization_recommendations(self) -> List[str]:
        """Generate cost optimization recommendations."""
        recommendations = []
        
        # Analyze recent usage patterns
        recent_hours = sorted(self.cost_metrics.keys())[-24:]
        if len(recent_hours) < 12:
            return ["Need more data for recommendations"]
        
        hourly_costs = [self.cost_metrics[hour]['cost'] for hour in recent_hours]
        hourly_usage = [self.cost_metrics[hour]['active_users'] for hour in recent_hours]
        
        # Check for underutilization
        avg_cost = sum(hourly_costs) / len(hourly_costs)
        avg_usage = sum(hourly_usage) / len(hourly_usage)
        current_capacity = self.current_profile.max_concurrent_users
        
        utilization_rate = avg_usage / current_capacity
        
        if utilization_rate < 0.3:
            recommendations.append("Consider scaling down - average utilization is below 30%")
        elif utilization_rate > 0.9:
            recommendations.append("Consider scaling up - average utilization is above 90%")
        
        # Check for cost spikes
        cost_variance = max(hourly_costs) - min(hourly_costs)
        if cost_variance > avg_cost * 0.5:
            recommendations.append("High cost variance detected - consider auto-scaling policies")
        
        # Check for consistent patterns
        peak_hours = [i for i, usage in enumerate(hourly_usage) if usage > avg_usage * 1.5]
        if len(peak_hours) > 0:
            recommendations.append(f"Peak usage detected at hours {peak_hours} - consider scheduled scaling")
        
        return recommendations

# Usage example
async def main():
    optimizer = CostOptimizer()
    
    # Start cost optimization monitoring
    optimization_task = asyncio.create_task(optimizer.monitor_usage_and_optimize())
    
    # Generate periodic reports
    while True:
        await asyncio.sleep(3600)  # Generate report every hour
        report = optimizer.generate_cost_report()
        print(f"Cost report: ${report['total_cost']:.2f} for {report['total_requests']} requests")
        
        for recommendation in report['recommendations']:
            print(f"Recommendation: {recommendation}")