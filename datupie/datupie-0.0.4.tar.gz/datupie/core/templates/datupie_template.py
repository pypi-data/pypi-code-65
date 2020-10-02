def data():    
    return dict({
        "project": "Project",
        "file":"Project",
        "architecture": {
            "terraform": {
                "required_providers": {
                    "aws": {
                        "source": "hashicorp/aws"
                    }
                }
            },
            "provider": {
                "aws": {
                    "profile": "default",
                    "region": "us-east-1"
                }
            },
            "resource": {
                "aws_s3_bucket":{
                    "project-datalake":{
                        "bucket":"project-datalake",
                        "acl":"private"
                    }
                },
                "aws_codecommit_repository":{
                    "project-repository":{
                        "repository_name":"project-repository",
                        "description":"This is a repository created by DatupieHW under Terraform"
                    }
                },
                "aws_s3_bucket_object":{
                    "dev_enviroment":{
                        "bucket":"project-datalake",
                        "key":"dev/",
                        "force_destroy":True
                    },
                    "dev_enviroment_clean":{
                        "bucket":"project-datalake",
                        "key":"dev/clean/",
                        "force_destroy":True
                    },
                    "dev_enviroment_prepare":{
                        "bucket":"project-datalake",
                        "key":"dev/prepare/",
                        "force_destroy":True
                    },
                    "dev_enviroment_transform":{
                        "bucket":"project-datalake",
                        "key":"dev/transform/",
                        "force_destroy":True
                    },
                    "dev_enviroment_inference":{
                        "bucket":"project-datalake",
                        "key":"dev/inference/",
                        "force_destroy":True
                    },
                    "dev_enviroment_data":{
                        "bucket":"project-datalake",
                        "key":"dev/data/",
                        "force_destroy":True
                    },
                    "prod_enviroment":{
                        "bucket":"project-datalake",
                        "key":"prod/",
                        "force_destroy":True
                    },
                    "prod_enviroment_inference":{
                        "bucket":"project-datalake",
                        "key":"prod/inference/",
                        "force_destroy":True
                    }
                }
            }
        }
    })