# Cloud Native Deployment Guide

This document details the steps required to deploy the Green-AI Agent onto a Kubernetes cluster.

## Prerequisites
- A running Kubernetes cluster (e.g., kind, minikube, EKS, GKE, AKS).
- `kubectl` installed and configured to communicate with your cluster.
- (Optional) `helm` installed for Helm chart deployment.

## Deploying via `kubectl apply`

The Kubernetes manifests are located in the `deploy/kubernetes` directory. To deploy the Green-AI Agent, execute the following commands in order:

1. **Deployment**: Creates the replica set with appropriate resource limits and liveness/readiness probes.
   ```bash
   kubectl apply -f deploy/kubernetes/deployment.yaml
   ```

2. **Service**: Creates a ClusterIP service to expose the FastAPI UI internally.
   ```bash
   kubectl apply -f deploy/kubernetes/service.yaml
   ```

3. **Ingress**: Defines routing rules mapping to your domain. You may need an Ingress controller (e.g., NGINX) installed on your cluster.
   ```bash
   kubectl apply -f deploy/kubernetes/ingress.yaml
   ```

4. **Horizontal Pod Autoscaler (HPA)**: Configures autoscaling to scale the pods based on CPU utilization.
   ```bash
   kubectl apply -f deploy/kubernetes/hpa.yaml
   ```

To verify the deployment:
```bash
kubectl get all -l app=green-ai
```

## Helm Chart Alternatives

Alternatively, you can package the manifests into a Helm chart for easier management, versioning, and parameterization.

A standard Helm chart structure would look like this:
```text
green-ai-chart/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── hpa.yaml
```

Once defined, you can deploy using:
```bash
helm install green-ai ./green-ai-chart -f custom-values.yaml
```
# Green-AI Code Scanner GitHub Action

Scan your code for energy inefficiency and sustainability debt natively in your CI/CD pipeline using the Green-AI GitHub Action.

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `target` | Path(s) to scan. Space-separated. | No | `.` |
| `output` | Path to output file. | No | |
| `format` | Output format (`csv`, `json`, `html`, `pdf`). | No | |
| `config` | Path to `.green-ai.yaml` config file. | No | |
| `fail-on` | Fail the action if violations of this severity or higher are found (`critical`, `high`, `medium`, `low`). | No | |
| `git-url` | Git repository URL to scan. | No | |
| `branch` | Specific branch to checkout (for git-url). | No | |

## Outputs

This action does not currently define specific outputs in `action.yml`, but you can use the `output` file configured via the inputs in subsequent steps (e.g., uploading the report as an artifact).

## Example Workflow Usage

```yaml
name: Green-AI Scan

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Run Green-AI Scanner
        uses: green-ai/green-ai-action@main
        with:
          target: './src'
          fail-on: 'high'
          format: 'html'
          output: 'green-ai-report.html'

      - name: Upload Report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: green-ai-report
          path: green-ai-report.html
```
