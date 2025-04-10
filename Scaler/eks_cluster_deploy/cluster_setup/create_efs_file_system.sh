# retrieve vpc id
vpc_id=$(aws eks describe-cluster \
    --name smart-hpa \
    --query "cluster.resourcesVpcConfig.vpcId" \
    --output text)

# retrieve CIDR range for cluster vpc
cidr_range=$(aws ec2 describe-vpcs \
    --vpc-ids "$vpc_id" \
    --query "Vpcs[].CidrBlock" \
    --output text \
    --region ap-southeast-2)

# create a security group with an inbound rule that allows 
# inbound NFS traffic for EFS mount points
security_group_id=$(aws ec2 create-security-group \
    --group-name stateEfsSecurityGroup \
    --description "Smart HPA state storage security group" \
    --vpc-id "$vpc_id" \
    --output text)

aws ec2 authorize-security-group-ingress \
    --group-id "$security_group_id" \
    --protocol tcp \
    --port 2049 \
    --cidr "$cidr_range"

# create a file system
file_system_id=$(aws efs create-file-system \
    --region ap-southeast-2 \
    --performance-mode generalPurpose \
    --query 'FileSystemId' \
    --output text)

# show all running nodes in the cluster
# including those running addons only (skip them)
printf "Running nodes: \n"
echo "Running nodes: "
kubectl get nodes

# show the subnets
aws ec2 describe-subnets \
    --filters "Name=vpc-id,Values=$vpc_id" \
    --query 'Subnets[*].{SubnetId: SubnetId,AvailabilityZone: AvailabilityZone,CidrBlock: CidrBlock}' \
    --output table

echo "Add each mount target for the subnet that you want to mount EFS"


