REMOTE_ACCESS_ROLE = 'akeru-cloud-access'
ASSUMED_ROLE_TIMEOUT = 60 * 60
FEDERATED_USER_TIMEOUT = 60 * 60

EC2_TRUST_POLICY = """{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}"""

LAMBDA_TRUST_POLICY = """{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}"""