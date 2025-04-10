# create Amazon VPC with public subnet only 
# to avoid NAT gateway hour cost
aws cloudformation create-stack \
    --region ap-southeast-2 \
    --stack-name smart-hpa-vpc-stack \
    --template-url https://s3.us-west-2.amazonaws.com/amazon-eks/cloudformation/2020-10-29/amazon-eks-vpc-sample.yaml


# create a cluster IAM role
aws iam create-role \
    --role-name smartHPAClusterRole \
    --assume-role-policy-document file://"eks-cluster-role-trust-policy.json"


# attach the required AWS EKS IAM managed policy to it
aws iam attach-role-policy \
    --policy-arn arn:aws:iam::aws:policy/AmazonEKSClusterPolicy \
    --role-name smartHPAClusterRole


