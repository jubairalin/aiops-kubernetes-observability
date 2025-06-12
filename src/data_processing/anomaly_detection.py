import numpy as np
from sklearn.ensemble import IsolationForest
from src.utils.logger import get_logger

logger = get_logger(__name__)

class AnomalyDetector:
    def __init__(self, config):
        self.config = config
        self.models = {
            'cpu': IsolationForest(contamination=0.01),
            'memory': IsolationForest(contamination=0.01),
            'restarts': IsolationForest(contamination=0.01)
        }
        self.training_data = {key: [] for key in self.models.keys()}
        
    def train_models(self, historical_data):
        """Train anomaly detection models with historical data"""
        try:
            for metric in self.models.keys():
                values = [item[metric] for item in historical_data if metric in item]
                if values:
                    X = np.array(values).reshape(-1, 1)
                    self.models[metric].fit(X)
                    logger.info(f"Trained {metric} anomaly detection model")
        except Exception as e:
            logger.error(f"Error training models: {e}")
    
    def detect_anomalies(self, current_metrics):
        """Detect anomalies in current metrics"""
        anomalies = []
        for metric_data in current_metrics:
            pod_anomalies = {}
            for metric, value in metric_data.items():
                if metric in self.models and isinstance(value, (int, float)):
                    prediction = self.models[metric].predict([[value]])[0]
                    if prediction == -1:  # Anomaly detected
                        pod_anomalies[metric] = {
                            'value': value,
                            'score': self.models[metric].decision_function([[value]])[0]
                        }
            
            if pod_anomalies:
                anomalies.append({
                    'pod': metric_data['pod'],
                    'timestamp': metric_data['timestamp'],
                    'anomalies': pod_anomalies
                })
        
        return anomalies