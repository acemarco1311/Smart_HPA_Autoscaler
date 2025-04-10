# create node IAM role
aws iam create-role \
    --role-name smartHPANodeRole \
    --assume-role-policy-document file://"node-role-trust-policy.json"

# attach tthe reqquired managed IAM policies to the role
aws iam attach-role-policy \
    --policy-arn arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy \
    --role-name smartHPANodeRole

aws iam attach-role-policy \
    --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly \
    --role-name smartHPANodeRole

aws iam attach-role-policy \
    --policy-arn arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy \
    --role-name smartHPANodeRole
