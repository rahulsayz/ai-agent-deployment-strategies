class VerticalScaler:
    def __init__(self, k8s_client):
        self.k8s_client = k8s_client
        self.resource_profiles = {
            'light': {'cpu': '1', 'memory': '2Gi', 'gpu': 0},
            'medium': {'cpu': '2', 'memory': '4Gi', 'gpu': 0},
            'heavy': {'cpu': '4', 'memory': '8Gi', 'gpu': 1},
            'gpu_intensive': {'cpu': '6', 'memory': '16Gi', 'gpu': 2}
        }
    
    async def analyze_workload_requirements(self, recent_requests: List[Dict]) -> str:
        """Analyze recent requests to determine optimal resource profile."""
        avg_processing_time = sum(req['processing_time'] for req in recent_requests) / len(recent_requests)
        gpu_usage_required = any(req.get('requires_gpu', False) for req in recent_requests)
        memory_intensive = any(req.get('large_context', False) for req in recent_requests)
        
        if gpu_usage_required and (avg_processing_time > 10 or memory_intensive):
            return 'gpu_intensive'
        elif gpu_usage_required or avg_processing_time > 5:
            return 'heavy'
        elif avg_processing_time > 2 or memory_intensive:
            return 'medium'
        else:
            return 'light'
    
    async def update_deployment_resources(self, deployment_name: str, 
                                        profile_name: str, namespace: str = 'default'):
        """Update Kubernetes deployment with new resource allocation."""
        profile = self.resource_profiles[profile_name]
        
        # Get current deployment
        deployment = await self.k8s_client.read_namespaced_deployment(
            name=deployment_name, namespace=namespace
        )
        
        # Update resource requirements
        container = deployment.spec.template.spec.containers[0]
        container.resources.requests = profile
        container.resources.limits = {
            'cpu': str(int(profile['cpu']) * 1.5),
            'memory': profile['memory'],
            'nvidia.com/gpu': profile['gpu']
        }
        
        # Apply updates
        await self.k8s_client.patch_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            body=deployment
        )
        
        print(f"Updated deployment {deployment_name} to {profile_name} profile")