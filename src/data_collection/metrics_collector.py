import time
from prometheus_api_client import PrometheusConnect
from src.utils.logger import get_logger
from src.utils.k8s_client import KubernetesClient

logger = get_logger(__name__)

class MetricsCollector:
    def __init__(self, config):
        self.config = config
        self.prometheus = PrometheusConnect(url=config['prometheus']['url'])
        self.k8s_client = KubernetesClient(config['kubernetes'])
        
    def collect_pod_metrics(self):
        """Collect key metrics for all pods in the namespace"""
        while True:
            try:
                pods = self.k8s_client.list_pods()
                metrics_data = []
                
                for pod in pods:
                    pod_name = pod.metadata.name
                    pod_metrics = {
                        'pod': pod_name,
                        'timestamp': time.time(),
                        'cpu_usage': self._get_cpu_usage(pod_name),
                        'memory_usage': self._get_memory_usage(pod_name),
                        'network_rx': self._get_network_rx(pod_name),
                        'network_tx': self._get_network_tx(pod_name),
                        'restarts': self._get_restart_count(pod_name)
                    }
                    metrics_data.append(pod_metrics)
                
                logger.info(f"Collected metrics for {len(pods)} pods")
                return metrics_data
                
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
            time.sleep(self.config['monitoring']['metrics_interval'])
    
    def _get_cpu_usage(self, pod_name):
        query = f'sum(rate(container_cpu_usage_seconds_total{{pod="{pod_name}"}}[1m])) by (pod)'
        return self._execute_prom_query(query)
    
    def _get_memory_usage(self, pod_name):
        query = f'sum(container_memory_working_set_bytes{{pod="{pod_name}"}}) by (pod)'
        return self._execute_prom_query(query)
    
    def _execute_prom_query(self, query):
        try:
            result = self.prometheus.custom_query(query)
            return float(result[0]['value'][1]) if result else 0.0
        except Exception as e:
            logger.error(f"Error executing Prometheus query: {e}")
            return 0.0