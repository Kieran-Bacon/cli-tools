@ECHO OFF
aws ecr get-login-password --region eu-west-2 --profile desc-admin | docker login --username AWS --password-stdin *.dkr.ecr.eu-west-2.amazonaws.com