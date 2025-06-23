# AWS EKS cluster configuration with GPU node groups
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: ai-agent-cluster
  region: us-west-2
  version: "1.24"

nodeGroups:
  - name: gpu-workers
    instanceType: p3.2xlarge
    desiredCapacity: 2
    minSize: 1
    maxSize: 10
    volumeSize: 100
    volumeType: gp3
    iam:
      withAddonPolicies:
        autoScaler: true
        cloudWatch: true
        ebs: true
    labels:
      node-type: gpu
      workload: ai-inference
    taints:
      - key: nvidia.com/gpu
        value: "true"
        effect: NoSchedule
    tags:
      Environment: production
      Team: ai-platform
    
  - name: cpu-workers
    instanceType: c5.4xlarge
    desiredCapacity: 3
    minSize: 2
    maxSize: 20
    labels:
      node-type: cpu
      workload: general