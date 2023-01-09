# Pre-requirements
- [Docker](https://www.docker.com/)
- [Kind](https://kind.sigs.k8s.io/)


# Installation

```shell
kind delete cluster --name argo-learning
kind create cluster --name argo-learning
kubectl config set-context kind-argo-learning
kubectl create ns argo
kubectl apply -n argo -f https://github.com/argoproj/argo-workflows/releases/download/v3.4.4/install.yaml
kubectl -n argo wait deploy --all --for condition=Available --timeout 2m
kubectl patch deployment \
  argo-server \
  --namespace argo \
  --type='json' \
  -p='[{"op": "replace", "path": "/spec/template/spec/containers/0/args", "value": [
  "server",
  "--auth-mode=server",
  "--secure=false"
]},
{"op": "replace", "path": "/spec/template/spec/containers/0/readinessProbe/httpGet/scheme", "value": "HTTP"}
]'
kubectl -n argo rollout status --watch --timeout=600s deployment/argo-server
```

### port forwarding to the UI
```shell
kubectl -n argo port-forward --address 0.0.0.0 svc/argo-server 2746:2746 > /dev/null &
```

# Authentication
```shell
kubectl apply -f ./workflow-role.yaml
kubectl create sa argo-user
kubectl create rolebinding argo-user --role=argo-user --serviceaccount=default:argo-user
kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: argo-user.service-account-token
  annotations:
    kubernetes.io/service-account.name: argo-user
type: kubernetes.io/service-account-token
EOF
unset ARGO_TOKEN
export ARGO_TOKEN="Bearer $(kubectl get secret argo-user.service-account-token -o=jsonpath='{.data.token}' | base64 --decode)"
echo $ARGO_TOKEN
```


# Building and loading custom image to kind
```shell
docker build -t generator:local .
kind load docker-image generator:local --name argo-learning
 ```

# Run example
```shell
# generate 1 workflow with 10 tasks multiplying numbers by 2
python ./workflows/main.py 1 10 2
```


# Links :
- [Hera Examples](https://github.com/argoproj-labs/hera-workflows/tree/main/examples)