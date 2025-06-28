import boto3
import sys
import time
import os

GITHUB_PAT = os.getenv("GITHUB_PAT")
if not GITHUB_PAT:
    raise Exception("Missing GitHub token in GITHUB_PAT environment variable.")

repo_full = sys.argv[1]  # Format: user/repo
branch = sys.argv[2]
repo_owner, repo_name = repo_full.split('/')
app_name = f"amplify-{repo_name}"

client = boto3.client('amplify','us-east-1')
print(GITHUB_PAT)

# Create Amplify App
app_response = client.create_app(
    name=app_name,
    repository=f"https://github.com/{repo_owner}/{repo_name}",
    oauthToken=GITHUB_PAT,
    platform='WEB',
    enableBranchAutoBuild=True
)
app_id = app_response['app']['appId']
print(f"[✓] Created Amplify app with ID: {app_id}")

# Create Branch
branch_response = client.create_branch(
    appId=app_id,
    branchName=branch,
    framework='React',
    enableAutoBuild=True
)
print(f"[✓] Created branch '{branch}'")

# Start Deployment
deploy_response = client.start_job(
    appId=app_id,
    branchName=branch,
    jobType='RELEASE',
    jobReason='Manual deployment from GitHub Actions'
)
job_id = deploy_response['jobSummary']['jobId']
print(f"[🚀] Deployment started. Job ID: {job_id}")

# Monitor
while True:
    status = client.get_job(appId=app_id, branchName=branch, jobId=job_id)['job']['summary']['status']
    print(f"→ Status: {status}")
    if status in ['SUCCEED', 'FAILED', 'CANCELLED']:
        print(f"[✔] Final Status: {status}")
        break
    time.sleep(10)

domain_name = 'www.apainewsbrief.in'

response = client.create_domain_association(
    appId=app_id,
    domainName=domain_name,
    subDomainSettings=[
        {
            'prefix': '',   # '' for root domain, or 'www', 'app', etc.
            'branchName': branch
        },
    ]
)

print("Custom domain association started:", response['domainAssociation']['domainName'])
