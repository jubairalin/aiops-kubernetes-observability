import dash
from dash import dcc, html
import plotly.graph_objs as go
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ObservabilityDashboard:
    def __init__(self, data_provider):
        self.app = dash.Dash(__name__)
        self.data_provider = data_provider
        self._setup_layout()
        
    def _setup_layout(self):
        """Set up the dashboard layout"""
        self.app.layout = html.Div([
            html.H1("Kubernetes Pod Observability Dashboard"),
            dcc.Tabs([
                dcc.Tab(label='Metrics', children=[
                    dcc.Graph(id='cpu-usage-graph'),
                    dcc.Graph(id='memory-usage-graph')
                ]),
                dcc.Tab(label='Anomalies', children=[
                    html.Div(id='anomalies-table')
                ]),
                dcc.Tab(label='Logs', children=[
                    html.Div(id='logs-viewer')
                ])
            ]),
            dcc.Interval(
                id='interval-component',
                interval=60*1000,  # Update every minute
                n_intervals=0
            )
        ])
        
        # Setup callbacks
        self.app.callback(
            dash.dependencies.Output('cpu-usage-graph', 'figure'),
            [dash.dependencies.Input('interval-component', 'n_intervals')]
        )(self._update_cpu_graph)
        
        # Add similar callbacks for other components
        
    def _update_cpu_graph(self, n):
        """Update CPU usage graph"""
        try:
            metrics = self.data_provider.get_recent_metrics()
            pods = list(set(m['pod'] for m in metrics))
            
            data = []
            for pod in pods:
                pod_metrics = [m for m in metrics if m['pod'] == pod]
                data.append(go.Scatter(
                    x=[m['timestamp'] for m in pod_metrics],
                    y=[m['cpu_usage'] for m in pod_metrics],
                    name=pod,
                    mode='lines+markers'
                ))
            
            return {
                'data': data,
                'layout': go.Layout(
                    title='CPU Usage by Pod',
                    xaxis={'title': 'Time'},
                    yaxis={'title': 'CPU Usage (cores)'}
                )
            }
        except Exception as e:
            logger.error(f"Error updating CPU graph: {e}")
            return {}
    
    def run(self, host='0.0.0.0', port=8050):
        """Run the dashboard server"""
        self.app.run_server(host=host, port=port)