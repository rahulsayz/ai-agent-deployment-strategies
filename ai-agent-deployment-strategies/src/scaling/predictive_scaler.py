import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pandas as pd

class PredictiveScaler:
    def __init__(self, history_window: int = 168):  # 1 week in hours
        self.history_window = history_window
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.metrics_history = []
    
    def collect_metrics(self, timestamp: float, request_count: int, 
                       response_time: float, cpu_usage: float, 
                       memory_usage: float, gpu_usage: float):
        """Collect metrics for training the predictive model."""
        self.metrics_history.append({
            'timestamp': timestamp,
            'hour_of_day': pd.to_datetime(timestamp, unit='s').hour,
            'day_of_week': pd.to_datetime(timestamp, unit='s').dayofweek,
            'request_count': request_count,
            'response_time': response_time,
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'gpu_usage': gpu_usage
        })
        
        # Keep only recent history
        if len(self.metrics_history) > self.history_window * 24:  # 24 data points per hour
            self.metrics_history = self.metrics_history[-self.history_window * 24:]
    
    def train_model(self):
        """Train the predictive scaling model."""
        if len(self.metrics_history) < 48:  # Need at least 2 days of data
            return False
        
        df = pd.DataFrame(self.metrics_history)
        
        # Feature engineering
        features = [
            'hour_of_day', 'day_of_week', 'request_count',
            'response_time', 'cpu_usage', 'memory_usage', 'gpu_usage'
        ]
        
        # Add lag features
        for col in ['request_count', 'response_time', 'cpu_usage']:
            df[f'{col}_lag_1h'] = df[col].shift(4)  # 1 hour ago (15min intervals)
            df[f'{col}_lag_24h'] = df[col].shift(96)  # 24 hours ago
            features.extend([f'{col}_lag_1h', f'{col}_lag_24h'])
        
        # Remove rows with NaN values
        df = df.dropna()
        
        if len(df) < 24:
            return False
        
        X = df[features]
        y = df['request_count'].shift(-4)  # Predict 1 hour ahead
        
        # Remove last 4 rows (no target values)
        X = X[:-4]
        y = y[:-4]
        
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        return True
    
    def predict_scaling_need(self, current_instances: int) -> int:
        """Predict the number of instances needed for the next hour."""
        if not self.is_trained:
            return current_instances
        
        # Get latest metrics
        latest_metrics = self.metrics_history[-1]
        current_time = time.time()
        
        features = [
            pd.to_datetime(current_time, unit='s').hour,
            pd.to_datetime(current_time, unit='s').dayofweek,
            latest_metrics['request_count'],
            latest_metrics['response_time'],
            latest_metrics['cpu_usage'],
            latest_metrics['memory_usage'],
            latest_metrics['gpu_usage']
        ]
        
        # Add lag features
        if len(self.metrics_history) >= 96:
            features.extend([
                self.metrics_history[-4]['request_count'],  # 1 hour ago
                self.metrics_history[-4]['response_time'],
                self.metrics_history[-4]['cpu_usage'],
                self.metrics_history[-96]['request_count'],  # 24 hours ago
                self.metrics_history[-96]['response_time'],
                self.metrics_history[-96]['cpu_usage']
            ])
        else:
            features.extend([0, 0, 0, 0, 0, 0])  # Default values
        
        features_scaled = self.scaler.transform([features])
        predicted_requests = self.model.predict(features_scaled)[0]
        
        # Convert predicted requests to required instances
        # Assuming each instance can handle 100 requests per hour
        required_instances = max(1, int(np.ceil(predicted_requests / 100)))
        
        return required_instances