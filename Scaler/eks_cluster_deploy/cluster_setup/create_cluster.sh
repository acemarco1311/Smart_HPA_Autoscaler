# create new cluster
aws eks create-cluster \
    --region ap-southeast-2 \
    --name smart-hpa \
    --kubernetes-version 1.32 \
    --role-arm arn:aws:iam::843300524918:role/smartHPAClusterRole \
    --resoures-vpc-config subnetIds=subnet-061f39faaa20c7a56, subnet-0f11bb720dd3624c9, subnet-01839ea76c5e93ed0, endpointPublicAccess=true, endpointPrivateAccess=false \
    --ip-family IPv4 \
    --add-ons aws-efs-csi-driver

# wait for the cluster to be created
aws eks wait cluster-active --name smart-hpa

# configure kubeconfig, change context from docker-desktop to cluster
aws eks update-kubeconfig --name smart-hpa --region ap-southeast-2

# install community metric server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
