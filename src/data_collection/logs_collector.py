from kubernetes import client, config
from src.utils.logger import get_logger

logger = get_logger(__name__)

class LogsCollector:
    def __init__(self, k8s_config):
        self.k8s_config = k8s_config
        config.load_kube_config(context=k8s_config['context'])
        self.core_api = client.CoreV1Api()
        
    def collect_pod_logs(self, pod_name, namespace=None):
        """Collect logs for a specific pod"""
        namespace = namespace or self.k8s_config['namespace']
        try:
            logs = self.core_api.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                tail_lines=100
            )
            return self._process_logs(logs, pod_name)
        except Exception as e:
            logger.error(f"Error collecting logs for pod {pod_name}: {e}")
            return []
    
    def _process_logs(self, raw_logs, pod_name):
        """Process raw logs into structured format"""
        processed_logs = []
        for line in raw_logs.split('\n'):
            if line.strip():
                processed_logs.append({
                    'timestamp': self._extract_timestamp(line),
                    'pod': pod_name,
                    'message': line,
                    'severity': self._classify_severity(line)
                })
        return processed_logs
    
    def _extract_timestamp(self, log_line):
        # Implement timestamp extraction logic
        return "2023-01-01T00:00:00Z"  # Placeholder
    
    def _classify_severity(self, log_line):
        # Implement simple severity classification
        if "error" in log_line.lower():
            return "error"
        elif "warn" in log_line.lower():
            return "warning"
        return "info"