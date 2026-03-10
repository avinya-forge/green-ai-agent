import os
import pytest
import subprocess
import requests
import time

KUBERNETES_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'deploy', 'kubernetes')

def test_kubernetes_manifest_validity():
    import yaml

    # Load and validate deployment
    deployment_path = os.path.join(KUBERNETES_DIR, 'deployment.yaml')
    assert os.path.exists(deployment_path)
    with open(deployment_path) as f:
        docs = list(yaml.safe_load_all(f))
        assert len(docs) == 1
        deployment = docs[0]
        assert deployment['kind'] == 'Deployment'

        # Validate spec limits
        resources = deployment['spec']['template']['spec']['containers'][0]['resources']
        assert resources['limits']['cpu'] == '500m'
        assert resources['limits']['memory'] == '512Mi'
        assert resources['requests']['cpu'] == '500m'
        assert resources['requests']['memory'] == '512Mi'

        # Validate probes
        liveness = deployment['spec']['template']['spec']['containers'][0]['livenessProbe']
        assert liveness['httpGet']['path'] == '/api/health'

        readiness = deployment['spec']['template']['spec']['containers'][0]['readinessProbe']
        assert readiness['httpGet']['path'] == '/api/health'

    # Load and validate service
    service_path = os.path.join(KUBERNETES_DIR, 'service.yaml')
    assert os.path.exists(service_path)
    with open(service_path) as f:
        docs = list(yaml.safe_load_all(f))
        assert len(docs) == 1
        service = docs[0]
        assert service['kind'] == 'Service'
        assert service['spec']['type'] == 'ClusterIP'

    # Load and validate ingress
    ingress_path = os.path.join(KUBERNETES_DIR, 'ingress.yaml')
    assert os.path.exists(ingress_path)
    with open(ingress_path) as f:
        docs = list(yaml.safe_load_all(f))
        assert len(docs) == 1
        ingress = docs[0]
        assert ingress['kind'] == 'Ingress'

    # Load and validate hpa
    hpa_path = os.path.join(KUBERNETES_DIR, 'hpa.yaml')
    assert os.path.exists(hpa_path)
    with open(hpa_path) as f:
        docs = list(yaml.safe_load_all(f))
        assert len(docs) == 1
        hpa = docs[0]
        assert hpa['kind'] == 'HorizontalPodAutoscaler'
        assert hpa['spec']['minReplicas'] == 1
        assert hpa['spec']['maxReplicas'] == 5

        metrics = hpa['spec']['metrics']
        assert len(metrics) > 0
        assert metrics[0]['resource']['target']['averageUtilization'] == 70
