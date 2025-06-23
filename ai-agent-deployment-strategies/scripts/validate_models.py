# scripts/validate_model_performance.py
import json
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics import accuracy_score, f1_score
import time

class ModelValidator:
    def __init__(self, model_path: str, test_dataset_path: str):
        self.model_path = model_path
        self.test_dataset_path = test_dataset_path
        self.validation_results = {}
    
    def load_test_dataset(self):
        """Load validation dataset for model testing."""
        with open(self.test_dataset_path, 'r') as f:
            return json.load(f)
    
    def validate_model_accuracy(self):
        """Test model accuracy against known benchmarks."""
        print("Validating model accuracy...")
        
        # Load model and tokenizer
        tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        model = AutoModel.from_pretrained(self.model_path)
        model.eval()
        
        test_data = self.load_test_dataset()
        predictions = []
        ground_truth = []
        
        for sample in test_data:
            inputs = tokenizer(sample['input'], return_tensors='pt', padding=True, truncation=True)
            
            with torch.no_grad():
                outputs = model(**inputs)
                prediction = torch.argmax(outputs.logits, dim=-1).item()
                predictions.append(prediction)
                ground_truth.append(sample['expected_output'])
        
        accuracy = accuracy_score(ground_truth, predictions)
        f1 = f1_score(ground_truth, predictions, average='weighted')
        
        self.validation_results['accuracy'] = accuracy
        self.validation_results['f1_score'] = f1
        
        # Set acceptance thresholds
        if accuracy < 0.85:
            raise ValueError(f"Model accuracy {accuracy:.3f} below threshold 0.85")
        if f1 < 0.80:
            raise ValueError(f"Model F1 score {f1:.3f} below threshold 0.80")
        
        print(f"Model validation passed: Accuracy={accuracy:.3f}, F1={f1:.3f}")
    
    def validate_inference_speed(self):
        """Test model inference performance."""
        print("Validating inference speed...")
        
        tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        model = AutoModel.from_pretrained(self.model_path)
        model.eval()
        
        # Test with various input sizes
        test_inputs = [
            "Short input text",
            "Medium length input text that represents typical user queries and requests",
            "Very long input text " * 50  # Simulate long context
        ]
        
        inference_times = []
        
        for input_text in test_inputs:
            inputs = tokenizer(input_text, return_tensors='pt', padding=True, truncation=True)
            
            # Warm-up run
            with torch.no_grad():
                model(**inputs)
            
            # Timed runs
            start_time = time.time()
            for _ in range(10):
                with torch.no_grad():
                    model(**inputs)
            avg_time = (time.time() - start_time) / 10
            inference_times.append(avg_time)
        
        max_inference_time = max(inference_times)
        self.validation_results['max_inference_time'] = max_inference_time
        
        # Check performance threshold
        if max_inference_time > 2.0:  # 2 second threshold
            raise ValueError(f"Max inference time {max_inference_time:.3f}s exceeds threshold 2.0s")
        
        print(f"Inference speed validation passed: Max time={max_inference_time:.3f}s")
    
    def save_validation_report(self):
        """Save validation results for CI/CD pipeline."""
        with open('model_validation_report.json', 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        
        print("Validation report saved to model_validation_report.json")

if __name__ == "__main__":
    validator = ModelValidator(
        model_path="./models/production_model",
        test_dataset_path="./data/validation_dataset.json"
    )
    
    validator.validate_model_accuracy()
    validator.validate_inference_speed()
    validator.save_validation_report()