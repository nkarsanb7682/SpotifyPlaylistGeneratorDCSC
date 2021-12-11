# Helm
# Open localhost:80
helm install prometheus prometheus-community/kube-prometheus-stack
kubectl apply -f grafana-ingress.yaml
