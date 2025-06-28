import boto3
import json
import os

REGION = "us-east-1"
STAGE = "prod"
ACCOUNT_ID = "269854564686"

apigateway = boto3.client("apigateway", region_name=REGION)
lambda_client = boto3.client("lambda", region_name=REGION)

def get_or_create_api(api_name):
    apis = apigateway.get_rest_apis()["items"]
    for api in apis:
        if api["name"] == api_name:
            print(f"Found API: {api_name}")
            return api["id"]

    print(f"Creating API: {api_name}")
    response = apigateway.create_rest_api(name=api_name)
    return response["id"]

def get_or_create_resource(api_id, resource_path):
    resources = apigateway.get_resources(restApiId=api_id)["items"]
    root_id = next(item["id"] for item in resources if item["path"] == "/")

    for res in resources:
        if res["path"] == f"/{resource_path}":
            print(f"Found resource: /{resource_path}")
            return res["id"]

    print(f"Creating resource: /{resource_path}")
    response = apigateway.create_resource(
        restApiId=api_id,
        parentId=root_id,
        pathPart=resource_path
    )
    return response["id"]

def method_exists(api_id, resource_id, http_method):
    try:
        apigateway.get_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod=http_method
        )
        return True
    except apigateway.exceptions.NotFoundException:
        return False

def add_lambda_permission(lambda_name, api_id, method, path):
    statement_id = f"{lambda_name.lower()}-{method.lower()}"
    try:
        lambda_client.add_permission(
            FunctionName=lambda_name,
            StatementId=statement_id,
            Action="lambda:InvokeFunction",
            Principal="apigateway.amazonaws.com",
            SourceArn=f"arn:aws:execute-api:{REGION}:{ACCOUNT_ID}:{api_id}/*/{method}/{path}"
        )
        print(f"Added permission to Lambda {lambda_name} for method {method} /{path}")
    except lambda_client.exceptions.ResourceConflictException:
        # Permission already exists
        print(f"Permission already exists for Lambda {lambda_name} and method {method} /{path}")

def setup_method(api_id, resource_id, method_def, path):
    method = method_def["httpMethod"].upper()
    lambda_name = method_def["lambdaFunctionName"]
    auth_type = method_def.get("authorizationType", "NONE")
    lambda_arn = f"arn:aws:lambda:{REGION}:{ACCOUNT_ID}:function:{lambda_name}"

    if method_exists(api_id, resource_id, method):
        print(f"Method {method} already exists for /{path}, skipping method creation.")
    else:
        print(f"Creating method {method} for /{path}")
        apigateway.put_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod=method,
            authorizationType=auth_type
        )

    print(f"Setting integration for {method} /{path}")
    apigateway.put_integration(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod=method,
        type="AWS_PROXY",
        integrationHttpMethod="POST",
        uri=f"arn:aws:apigateway:{REGION}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
    )

    add_lambda_permission(lambda_name, api_id, method, path)

def deploy_api(api_id):
    print(f"Deploying API {api_id} to stage: {STAGE}")
    apigateway.create_deployment(
        restApiId=api_id,
        stageName=STAGE
    )

def main():
    # Use script folder as working directory to find JSON files
    script_dir = os.path.dirname(os.path.abspath(__file__))

    deploy_apis = set()

    # Loop all JSON files in current folder
    for file in os.listdir(script_dir):
        if not file.endswith(".json"):
            continue

        json_path = os.path.join(script_dir, file)
        with open(json_path) as f:
            config = json.load(f)

        api_name = config["apiName"]
        resource_path = config["resourcePath"]
        method_def = config["method"]
        should_deploy = config.get("deploy", False)

        api_id = get_or_create_api(api_name)
        resource_id = get_or_create_resource(api_id, resource_path)
        setup_method(api_id, resource_id, method_def, resource_path)

        if should_deploy:
            deploy_apis.add(api_id)

    for api_id in deploy_apis:
        deploy_api(api_id)

if __name__ == "__main__":
    main()