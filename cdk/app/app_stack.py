from aws_cdk import (
    Stack,
    Tags,
    aws_codebuild as codebuild,
    aws_codedeploy as codedeploy,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_s3 as s3,
)
from constructs import Construct


class AppStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # api.RestApi(self, "CodeBuildApi")

        vpc = ec2.Vpc(
            self,
            "Vpc",
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/24"),
            nat_gateways=0,
            max_azs=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=27,
                )
            ],
        )
        # ec2_sg = ec2.SecurityGroup(self, "Ec2Sg", allow_all_outbound=True)
        instance = ec2.Instance(
            self,
            "Instance",
            machine_image=ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2),
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MICRO),
            vpc=vpc,
            vpc_subnets={"subnet_type": ec2.SubnetType.PUBLIC},
            propagate_tags_to_volume_on_creation=True,
            ssm_session_permissions=True,
        )
        Tags.of(instance).add("env", "demo")

        # CI/CD 周り
        artifacts_bucket = s3.Bucket(self, "ArtifactsBucket")
        project = codebuild.Project(
            self, "Project", source=codebuild.Source.s3(bucket=artifacts_bucket, path="artifacts.zip")
        )
        code_deploy_role = iam.Role(
            self, "CodeDeployRole", assumed_by=iam.ServicePrincipal("codedeploy.amazonaws.com")
        )
        application = codedeploy.ServerApplication(self, "CodeDeployApplication", application_name="github-handson")
        deployment_group = codedeploy.ServerDeploymentGroup(
            self,
            "CodeDeployDeploymentGroup",
            application=application,
            deployment_group_name="HandsonDeploymentGroup",
            install_agent=True,
            ec2_instance_tags=codedeploy.InstanceTagSet({"env": ["demo"]}),
        )
