from aws_cdk import (
    Stack,
    Tags,
    aws_cloudtrail as cloudtrail,
    aws_codebuild as codebuild,
    aws_codedeploy as codedeploy,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_action,
    aws_ec2 as ec2,
    aws_s3 as s3,
)
from constructs import Construct


class AppStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

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
        source_bucket = s3.Bucket(self, "SourceBucket", versioned=True)
        artifacts = codepipeline.Artifact("Artifact")
        key = "source"
        trail = cloudtrail.Trail(self, "CloudTrail")
        trail.add_s3_event_selector(
            [cloudtrail.S3EventSelector(bucket=source_bucket, object_prefix=key)],
            read_write_type=cloudtrail.ReadWriteType.WRITE_ONLY,
        )
        source_action = codepipeline_action.S3SourceAction(
            action_name="S3Source",
            bucket=source_bucket,
            bucket_key=key,
            output=artifacts,
            trigger=codepipeline_action.S3Trigger.EVENTS,
        )
        project = codebuild.PipelineProject(self, id="build-project", project_name="Project")
        # code_deploy_role = iam.Role(
        #     self, "CodeDeployRole", assumed_by=iam.ServicePrincipal("codedeploy.amazonaws.com")
        # )
        application = codedeploy.ServerApplication(self, "CodeDeployApplication", application_name="github-handson")
        deployment_group = codedeploy.ServerDeploymentGroup(
            self,
            "CodeDeployDeploymentGroup",
            application=application,
            deployment_group_name="HandsonDeploymentGroup",
            install_agent=True,
            ec2_instance_tags=codedeploy.InstanceTagSet({"env": ["demo"]}),
        )
        build_output = codepipeline.Artifact("BuildArtifact")
        build_action = codepipeline_action.CodeBuildAction(
            action_name="build", project=project, input=artifacts, outputs=[build_output]
        )
        deploy_action = codepipeline_action.CodeDeployServerDeployAction(
            action_name="deploy", deployment_group=deployment_group, input=artifacts
        )
        pipeline = codepipeline.Pipeline(self, "Pipeline", pipeline_name="pipeline")
        pipeline.add_stage(stage_name="source", actions=[source_action])
        pipeline.add_stage(stage_name="build", actions=[build_action])
        pipeline.add_stage(stage_name="deploy", actions=[deploy_action])
