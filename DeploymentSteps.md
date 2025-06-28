🛠️ Deployment Steps
1. Set Up VPC and Networking Components
Create a custom VPC with public and private subnets

Create VPC Endpoints for required AWS services
    S3 - com.amazonaws.us-east-1.s3
    Comprehend - com.amazonaws.us-east-1.comprehend
    Bedrock Agent - com.amazonaws.us-east-1.bedrock-agent-runtime

Set up Security Groups for:

RDS
Lambda
Comprehend
Endpoints ( If Required )

🧠 Tip: Use AWS CloudFormation, CDK, or Terraform to automate VPC setup.

2. Set Up IAM Roles
Create IAM roles with least-privilege policies:

LambdaExecutionRole
AmplifyServiceRole
DatabaseAccessRole (if needed for other services)

3. Deploy the Database (RDS)
Provision RDS (PostgreSQL)

Ensure it is deployed in private subnets of your VPC

Update Security Groups to allow Lambda access

Store DB credentials in AWS Secrets Manager or SSM

4. Deploy Lambda Functions and Layers
Package Lambda code and upload using Github Actions

If using a Lambda Layer (e.g., shared libraries or dependencies):

To deploy Layer - workflows/layer.yaml
    Pipeline automatically updates all the lambdas ( using the layer ) with the latest version of the layer

To Deploy Lambda - workflows/lambda.yaml
    Pipeline creates lambdas with all the parameters in the workflow file.
    Modify according to the use


5. Configure API Gateway
Create REST API

Connect routes to corresponding Lambda functions

To deploy API - workflows/layer.yaml

6. Deploy Frontend using Amplify
Push code to GitHub

To deploy fromtend - workflows/amplify.yaml

    Set Github PAT in the secrets manager.

    Pass the repo full name and branch to deploy as parameters

Actions builds and deploys your app with the custom domain


7. Post-Deployment Checklist
✅ Test API endpoints via Postman or cURL

✅ Confirm frontend is live via Amplify URL or Custom Domain

✅ Check RDS connectivity from Lambda

✅ Monitor logs in CloudWatch