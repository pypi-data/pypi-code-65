from unittest import TestCase, main
from aws import cluster, cfm, ec2
import boto3
import warnings


class Config:
    '''All the test parameters'''
    def __init__(self):
        self.vpc_name = 'bs'
        self.vpc_class = 'np'
        self.domain_name = 'bootstrap.simoncomputing.com'
        self.validation_domain = 'simoncomputing.com'
        self.cidr_prefix = '10.10'
        self.workers = 2
        self.password = 'password'
        self.app_name = 'bootstrapp'

CONFIG = Config()


def get_output(stack: dict, output_key: str):
    '''Helper function to get an OutputValue from the given stack'''
    return next((o['OutputValue'] for o in stack['Outputs'] if o.get('OutputKey') == output_key), None)


class TestCluster(TestCase):

    stacks = []
    buckets = []


    @classmethod
    def setUpClass(cls):
        # Hide ResourceWarnings spammed by boto3. This is a known issue and is harmless.
        warnings.simplefilter('ignore', category=ResourceWarning)


    def run(self, result=None):
        # Keep running tests only if no errors/failures
        if result and result.wasSuccessful():
            super(TestCluster, self).run(result)


    @classmethod
    def tearDownClass(cls):
        # Clean up all the created stacks and s3 buckets after running the test suite
        cls.stacks.reverse()
        for stack in cls.stacks:
            if type(stack) is dict and 'StackName' in stack:
                cfm.delete_stack(stack['StackName'])
        for bucket in cls.buckets:
            try:
                boto3.client('s3').delete_bucket(Bucket=bucket)
            except:
                pass


    ###########################################################################
    # create_certificate
    ###########################################################################

    def test_00a_create_certificate_invalid_vpc_class(self):
        with self.assertRaises(ValueError):
            cluster.create_certificate(CONFIG.vpc_name, 'garbage', CONFIG.domain_name, validation_domain=CONFIG.validation_domain)
    

    def test_00b_create_certificate_invalid_domain_name(self):
        with self.assertRaises(Exception):
            cert = cluster.create_certificate(CONFIG.vpc_name, CONFIG.vpc_class, 'garbage', validation_domain=CONFIG.validation_domain)
            cfm.delete_stack(cert['StackName'])

    
    def test_00c_create_certificate(self):
        cert = cluster.create_certificate(CONFIG.vpc_name, CONFIG.vpc_class, CONFIG.domain_name, validation_domain=CONFIG.validation_domain)
        self.stacks.append(cert)

        cert_arn = get_output(cert, 'OutputCertificate')
        self.assertIsNotNone(cert_arn, msg='Certificate ARN not found in output')

        try:
            boto3.client('acm').get_certificate(CertificateArn=cert_arn)
        except:
            self.fail(f'Could not find certificate with ARN: {cert_arn}. It may have not been created properly.')


    ###########################################################################
    # create_vpc
    ###########################################################################

    def test_01a_create_vpc_invalid_cidr(self):
        with self.assertRaises(Exception):
            stack = cluster.create_vpc(CONFIG.vpc_name, cidr_prefix='garbage')
            cfm.delete_stack(stack['StackName']) 


    def test_01b_create_vpc(self):
        vpc = cluster.create_vpc(CONFIG.vpc_name, cidr_prefix=CONFIG.cidr_prefix)
        self.stacks.append(vpc)
        
        vpcid = get_output(vpc, 'VPC')
        self.assertIsNotNone(ec2.get_vpc(vpcid=vpcid))


    ###########################################################################
    # create_cp
    ###########################################################################
    
    def test_02a_create_cp_unknown_vpc(self):
        with self.assertRaises(Exception):
            cp = cluster.create_cp('garbage')
            cfm.delete_stack(cp['StackName'])
    
    
    def test_02b_create_cp(self):
        cp = cluster.create_cp(CONFIG.vpc_name)
        self.stacks.append(cp)
        self.cp = cp

        cluster_name = get_output(cp, 'Cluster')

        try:
            boto3.client('eks').describe_cluster(name=cluster_name)
        except:
            self.fail(f'Could not find cluster: {cluster_name}. It may not have been created properly.')


    ###########################################################################
    # create_eks_workers
    ###########################################################################

    def test_03a_create_eks_workers_unknown_cp(self):
        with self.assertRaises(Exception):
            eks_workers = cluster.create_eks_workers('garbage', CONFIG.workers)
            cfm.delete_stack(eks_workers['StackName'])


    def test_03b_create_eks_workers(self):
        eks_workers = cluster.create_eks_workers(CONFIG.vpc_name, CONFIG.workers)
        self.stacks.append(eks_workers)

        cluster_name = get_output(eks_workers, 'ClusterName')
        nodegroup_name = get_output(eks_workers, 'NodegroupName')

        try:
            boto3.client('eks').describe_nodegroup(clusterName=cluster_name, nodegroupName=nodegroup_name)
        except:
            self.fail(f'Could not find nodegroup: {nodegroup_name}. It may not have been created properly.')


    ###########################################################################
    # create_rds
    ###########################################################################
    
    def test_04a_create_rds_unknown_vpc(self):
        with self.assertRaises(Exception):
            rds = cluster.create_rds('garbage')
            cfm.delete_stack(rds['StackName'])


    def test_04b_create_rds(self):
        rds = cluster.create_rds(CONFIG.vpc_name, password=CONFIG.password)
        self.stacks.append(rds)

        instance_id = get_output(rds, 'DBInstance')

        try:
            boto3.client('rds').describe_db_instances(DBInstanceIdentifier=instance_id)
        except:
            self.fail(f'Could not find RDS instance: {instance_id}. It may not have been created properly.')


    ###########################################################################
    # create_ecr
    ###########################################################################
    
    def test_05a_create_ecr(self):
        ecr = cluster.create_ecr(CONFIG.app_name)
        self.stacks.append(ecr)

        repo_name = get_output(ecr, 'Repository')

        try:
            boto3.client('ecr').describe_repositories(repositoryNames=[repo_name])
        except:
            self.fail(f'Could not find ECR repository: {repo_name}. It may not have been created properly')


    ###########################################################################
    # create_s3_storage
    ###########################################################################

    def test_06a_create_s3_storage_unknown_vpc(self):
        with self.assertRaises(ValueError):
            s3_storage = cluster.create_s3_storage('garbage', CONFIG.app_name)
            cfm.delete_stack(s3_storage['StackName'])


    def test_06b_create_s3_storage(self):
        s3_storage = cluster.create_s3_storage(CONFIG.vpc_name, CONFIG.app_name)
        self.stacks.append(s3_storage)

        bucket = get_output(s3_storage, 'Bucket')
        self.buckets.append(bucket)

        try:
            boto3.client('s3').list_objects(Bucket=bucket)
        except:
            self.fail(f'Could not find bucket {bucket}. It may not have been created properly.')


    ###########################################################################
    # create_s3_hosting
    ###########################################################################
    
    def test_07a_create_s3_hosting_unknown_vpc(self):
        with self.assertRaises(ValueError):
            s3_hosting = cluster.create_s3_hosting('garbage', CONFIG.app_name, CONFIG.domain_name)
            cfm.delete_stack(s3_hosting['StackName'])


    def test_07b_create_s3_hosting_no_cert(self):
        with self.assertRaises(Exception):
            s3_hosting = cluster.create_s3_hosting(CONFIG.vpc_name, CONFIG.app_name, 'domain.with.no.certificate')
            cfm.delete_stack(s3_hosting['StackName'])


    def test_07c_create_s3_hosting(self):
        s3_hosting = cluster.create_s3_hosting(CONFIG.vpc_name, CONFIG.app_name, CONFIG.domain_name)
        self.stacks.append(s3_hosting)

        bucket = get_output(s3_hosting, 'Bucket')
        self.buckets.append(bucket)

        try:
            boto3.client('s3').list_objects(Bucket=bucket)
        except:
            self.fail(f'Could not find bucket {bucket}. It may not have been created properly.')

        distribution = get_output(s3_hosting, 'Distribution')

        try:
            boto3.client('cloudfront').get_distribution(Id=distribution)
        except:
            self.fail(f'Could not find cloudfront distribution {distribution}. It may not have been created properly.')


if __name__ == "__main__":
    main()