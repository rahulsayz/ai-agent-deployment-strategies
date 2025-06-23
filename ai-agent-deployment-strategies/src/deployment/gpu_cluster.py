import torch
import torch.nn as nn
from torch.nn.parallel import DistributedDataParallel

class DistributedAIAgent:
    def __init__(self, model_config, world_size, rank):
        self.world_size = world_size
        self.rank = rank
        self.device = torch.device(f"cuda:{rank}")
        
        # Initialize distributed processing
        torch.distributed.init_process_group(
            backend='nccl',
            world_size=world_size,
            rank=rank
        )
        
        # Load model partition for this GPU
        self.model = self.load_model_partition(model_config)
        self.model = DistributedDataParallel(
            self.model.to(self.device),
            device_ids=[rank]
        )
    
    def load_model_partition(self, config):
        """Load appropriate model partition for this GPU."""
        if self.rank == 0:
            # Load embedding and first transformer layers
            return EmbeddingAndInitialLayers(config)
        elif self.rank == self.world_size - 1:
            # Load final layers and output head
            return FinalLayersAndOutput(config)
        else:
            # Load intermediate transformer layers
            return IntermediateLayers(config, self.rank)
    
    async def inference(self, input_data):
        """Perform distributed inference across GPU cluster."""
        with torch.no_grad():
            # Process through model pipeline
            if self.rank == 0:
                # First GPU: tokenization and initial processing
                encoded_input = self.model(input_data)
                torch.distributed.send(encoded_input, dst=1)
                return None
            
            elif self.rank == self.world_size - 1:
                # Last GPU: generate final output
                torch.distributed.recv(encoded_input, src=self.rank-1)
                output = self.model(encoded_input)
                return output
            
            else:
                # Intermediate GPUs: pass-through processing
                torch.distributed.recv(encoded_input, src=self.rank-1)
                processed = self.model(encoded_input)
                torch.distributed.send(processed, dst=self.rank+1)
                return None
class DataParallelAIAgent:
    def __init__(self, model_path, gpu_devices):
        self.gpu_devices = gpu_devices
        self.models = {}
        
        # Load model replica on each GPU
        for device_id in gpu_devices:
            self.models[device_id] = torch.load(model_path).to(f"cuda:{device_id}")
            self.models[device_id].eval()
        
        self.request_queue = asyncio.Queue()
        self.gpu_assignment = cycle(gpu_devices)
    
    async def process_request(self, request_data):
        """Route request to available GPU."""
        assigned_gpu = next(self.gpu_assignment)
        
        with torch.cuda.device(assigned_gpu):
            model = self.models[assigned_gpu]
            result = await self.run_inference(model, request_data)
            return result
    
    async def run_inference(self, model, data):
        """Execute model inference on assigned GPU."""
        with torch.no_grad():
            input_tensor = torch.tensor(data).cuda()
            output = model(input_tensor)
            return output.cpu().numpy()