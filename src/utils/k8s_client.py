from kubernetes import client, config
from kubernetes.client.rest import ApiException
from src.utils.logger import get_logger

logger = get_logger(__name__)

class KubernetesClient:
    def __init__(self, config):
        self.config = config
        self._load_config()
        
    def _load_config(self):
        """Load Kubernetes configuration"""
        try:
            config.load_kube_config(context=self.config['context'])
            self.core_api = client.CoreV1Api()
            self.apps_api = client.AppsV1Api()
        except Exception as e:
            logger.error(f"Error loading Kubernetes config: {e}")
            raise
    
    def list_pods(self, namespace=None):
        """List all pods in the namespace"""
        namespace = namespace or self.config['namespace']
        try:
            return self.core_api.list_namespaced_pod(namespace).items
        except ApiException as e:
            logger.error(f"Error listing pods: {e}")
            return []
    
    def get_pod_status(self, pod_name, namespace=None):
        """Get status of a specific pod"""
        namespace = namespace or self.config['namespace']
        try:
            pod = self.core_api.read_namespaced_pod_status(pod_name, namespace)
            return {
                'phase': pod.status.phase,
                'conditions': pod.status.conditions,
                'containers': [{
                    'name': c.name,
                    'ready': c.ready,
                    'restart_count': c.restart_count
                } for c in pod.status.container_statuses] if pod.status.container_statuses else []
            }
        except ApiException as e:
            logger.error(f"Error getting pod status: {e}")
            return None