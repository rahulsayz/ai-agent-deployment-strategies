import GPUtil
import psutil
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class GPUMetrics:
    gpu_id: int
    utilization: float
    memory_used: float
    memory_total: float
    temperature: float
    power_draw: float

class GPUResourceManager:
    def __init__(self, target_utilization: float = 0.8):
        self.target_utilization = target_utilization
        self.gpu_metrics_history = []
    
    def get_gpu_metrics(self) -> List[GPUMetrics]:
        """Collect comprehensive GPU metrics."""
        gpus = GPUtil.getGPUs()
        metrics = []
        
        for gpu in gpus:
            metrics.append(GPUMetrics(
                gpu_id=gpu.id,
                utilization=gpu.load,
                memory_used=gpu.memoryUsed,
                memory_total=gpu.memoryTotal,
                temperature=gpu.temperature,
                power_draw=getattr(gpu, 'powerDraw', 0)
            ))
        
        self.gpu_metrics_history.append(metrics)
        return metrics
    
    def find_optimal_gpu(self, memory_requirement: float) -> Optional[int]:
        """Find the best GPU for new workload placement."""
        metrics = self.get_gpu_metrics()
        
        available_gpus = [
            gpu for gpu in metrics
            if (gpu.memory_total - gpu.memory_used) >= memory_requirement
            and gpu.utilization < self.target_utilization
        ]
        
        if not available_gpus:
            return None
        
        # Select GPU with lowest current utilization
        optimal_gpu = min(available_gpus, key=lambda g: g.utilization)
        return optimal_gpu.gpu_id
    
    def should_scale_up(self) -> bool:
        """Determine if additional GPU resources are needed."""
        recent_metrics = self.gpu_metrics_history[-5:]  # Last 5 measurements
        
        if len(recent_metrics) < 5:
            return False
        
        avg_utilization = sum(
            sum(gpu.utilization for gpu in measurement) / len(measurement)
            for measurement in recent_metrics
        ) / len(recent_metrics)
        
        return avg_utilization > self.target_utilization