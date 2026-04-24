from pathlib import Path

import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_apigatewayv2 as apigwv2,
    aws_apigatewayv2_integrations as apigwv2_integrations,
    aws_ec2 as ec2,
    aws_efs as efs,
    aws_lambda as _lambda,
)
from constructs import Construct

DEMO_DIR = str(Path(__file__).resolve().parents[2] / "demo")

LAMBDA_ENV = {
    "DJANGO_DB_PATH": "/mnt/db/db.sqlite3",
    "DJANGO_ALLOWED_HOSTS": "*",
}


class DemoStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(
            self,
            "Vpc",
            max_azs=2,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Isolated",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24,
                ),
            ],
        )

        file_system = efs.FileSystem(
            self,
            "Fs",
            vpc=vpc,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        access_point = file_system.add_access_point(
            "Ap",
            path="/db",
            create_acl=efs.Acl(owner_uid="1000", owner_gid="1000", permissions="750"),
            posix_user=efs.PosixUser(uid="1000", gid="1000"),
        )

        lambda_fs = _lambda.FileSystem.from_efs_access_point(access_point, "/mnt/db")

        api_fn = _lambda.DockerImageFunction(
            self,
            "ApiFn",
            code=_lambda.DockerImageCode.from_image_asset(DEMO_DIR),
            vpc=vpc,
            filesystem=lambda_fs,
            memory_size=512,
            timeout=cdk.Duration.seconds(30),
            environment=LAMBDA_ENV,
        )

        migrate_fn = _lambda.DockerImageFunction(
            self,
            "MigrateFn",
            code=_lambda.DockerImageCode.from_image_asset(
                DEMO_DIR,
                cmd=["lambda_handler.migrate"],
            ),
            vpc=vpc,
            filesystem=lambda_fs,
            memory_size=512,
            timeout=cdk.Duration.minutes(2),
            environment=LAMBDA_ENV,
        )

        http_api = apigwv2.HttpApi(
            self,
            "HttpApi",
            default_integration=apigwv2_integrations.HttpLambdaIntegration(
                "ApiIntegration", handler=api_fn
            ),
        )

        cdk.CfnOutput(self, "HttpApiUrl", value=http_api.api_endpoint)
        cdk.CfnOutput(self, "MigrateFunctionName", value=migrate_fn.function_name)
