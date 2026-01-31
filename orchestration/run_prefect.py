"""
Run Prefect server and deploy flows
"""
import subprocess
import sys
from pathlib import Path

def start_prefect_server():
    """Start Prefect server"""
    print("Starting Prefect server...")
    subprocess.run([sys.executable, "-m", "prefect", "server", "start"])

def deploy_flow():
    """Deploy the flow"""
    print("Deploying flow...")
    # Note: In production, you would use Prefect Cloud or self-hosted server
    # For local development, just run the flow directly
    from orchestration.dags.gaming_pipeline_dag import gaming_data_pipeline_flow
    gaming_data_pipeline_flow(limit_per_game=10, generate_forecasts=True)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        start_prefect_server()
    else:
        deploy_flow()
