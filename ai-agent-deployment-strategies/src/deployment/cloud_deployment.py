class HybridDeploymentManager:
    def __init__(self, cloud_config, on_prem_config):
        self.cloud_deployment = CloudAIAgent(cloud_config)
        self.on_prem_deployment = OnPremAIAgent(on_prem_config)
        self.routing_policy = self.load_routing_policy()
    
    async def route_request(self, request_data, user_context):
        """Route requests based on data sensitivity and performance requirements."""
        
        # Check data classification
        if self.contains_sensitive_data(request_data):
            return await self.on_prem_deployment.process(request_data)
        
        # Check current load and performance requirements
        if request_data.get('priority') == 'high':
            cloud_latency = await self.cloud_deployment.estimate_latency()
            on_prem_latency = await self.on_prem_deployment.estimate_latency()
            
            if on_prem_latency < cloud_latency:
                return await self.on_prem_deployment.process(request_data)
        
        # Default to cloud for scalability
        return await self.cloud_deployment.process(request_data)
    
    def contains_sensitive_data(self, data) -> bool:
        """Classify data sensitivity for routing decisions."""
        sensitive_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Credit card
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email
        ]
        
        content = str(data)
        return any(re.search(pattern, content) for pattern in sensitive_patterns)