import sys
import re

def apply_fixes(config):
    # Fix securityContext.runAsUser and securityContext.runAsGroup
    if 'securityContext' not in config:
        config += '''
      securityContext:
        runAsUser: 10001
        runAsGroup: 10001
        '''
    else:
        if 'runAsUser' not in config:
            config = re.sub(r'(securityContext:\n)', r'\1        runAsUser: 10001\n', config)
        if 'runAsGroup' not in config:
            config = re.sub(r'(securityContext:\n)', r'\1        runAsGroup: 10001\n', config)

    # Add readinessProbe if missing
    if 'readinessProbe' not in config:
        config = re.sub(r'(containers:\n        - name: .*)', r'\1\n          readinessProbe:\n            httpGet:\n              path: /healthz\n              port: 80\n            initialDelaySeconds: 5\n            periodSeconds: 5\n', config)
    
    # Fix container security context
    if 'securityContext' not in config:
        config += '''
          securityContext:
            runAsNonRoot: true
            capabilities:
              drop:
              - ALL
        '''
    else:
        if 'runAsNonRoot' not in config:
            config = re.sub(r'(securityContext:\n)', r'\1            runAsNonRoot: true\n', config)
        if 'capabilities' not in config:
            config = re.sub(r'(securityContext:\n)', r'\1            capabilities:\n              drop:\n              - ALL\n', config)
    
    # Add resource limits and requests
    if 'resources' not in config:
        config = re.sub(r'(containers:\n        - name: .*)', r'\1\n          resources:\n            limits:\n              cpu: "500m"\n              memory: "128Mi"\n            requests:\n              cpu: "250m"\n              memory: "64Mi"\n', config)

    # Set image tag to avoid latest
    config = re.sub(r'image: ".*:latest"', r'image: "image:1.0"', config)

    # Add NetworkPolicy section
    if 'networkPolicy' not in config:
        config += '''
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-same-namespace
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector: {}
        '''
    return config

def main(report_path, config_path):
    with open(report_path, 'r') as report_file:
        report = report_file.read()
    
    with open(config_path, 'r') as config_file:
        config = config_file.read()
    
    fixed_config = apply_fixes(config)
    
    with open(config_path, 'w') as config_file:
        config_file.write(fixed_config)

if __name__ == '__main__':
    report_path = sys.argv[1]
    config_path = sys.argv[2]
    main(report_path, config_path)
