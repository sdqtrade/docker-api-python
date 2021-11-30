<p align="center">
    <a href="http://www.sdqtrade.com/">
        <img alt="Docker API For Quantitative  Trading Platform" src="logo.png" width="150" style="max-width: 100%" />
    </a>
</p>
<p align="center">
    <a href="https://opensource.org/licenses/MIT">
        <img src="https://img.shields.io/badge/license-MIT-green" />
    </a>
</p>
<h1 align="center">Docker API For Quantitative  Trading Platform</h1>

## **正在寻找中文版本? [点击这里](./README_zh_CN.md)**

## Introduction
This repository is part of the Blue Quantitative Trading Platform. 
It provides the functionality to pack the strategy document, create image and environment setup.   

The internal service will communicate with http api. And the service is written by python.


Functionality：
* Pack the strategy document（python）
* Build docker image
* Push and execute the strategy inside docker
* Docker and environment maintenance and destory
  Use terraform to integrate with different cloud platform API to achive the automation of environemnt setup (Including server purchase, setup parameter, document image upload and application startup).
  
Supported cloud platform provider:
* Alibaba Cloud
* *AWS（Working in progress）*
* *Coming soon...*


## Quick Start
### 1.Install pip dependencies
```bash
pip install -r requirements.txt
```
### 2.[Install Docker](https://docs.docker.com/get-docker/)
### 3.[Install Terraform](https://www.terraform.io/downloads.html)

### 4.Start Service
```python
python app.py
```
### API
* POST http://localhost:6787/api

  The docker image will be created dynamically (depends on strategy content, docker properties, configuration file and cloud service provider credentials) and push to the destined cloud provider.
  

* POST http://localhost:6787/api/containers/stop

  Destroy the specified container or environment

## Terraform descriptions
### Directory
```bash
docker-api-python
└── terraform_shells
    └── alicloud
        ├── deploy.sh
        └── main.tf
        └── outputs.tf
        └── variables.tf
        └── vpc.tf
```
* terraform_shells - integration documents for different cloud service provider
* Use folders to seperate the cloud service provider
* Cloud platform integration files are written by terraform
* Using deploy.sh as the entry point of the shell


### deploy.sh entry point parameters
```bash
terraform init;
docker_registry_url=$1;
docker_registry_username=$2;
docker_registry_password=$3;
client_name=$4;
client_cloud=$5;
access_key=$6;
secret_key=$7;
deploy_action=$8;
file_name=$9
instance_name=$10
```
* docker_registry_url
* docker_registry_username
* docker_registry_password

  URL, user name and password for the docker registry

* client_name

  Name of the docker image

* client_cloud

  Name of Cloud service provider

* access_key
* secret_key

  API keys

* deploy_action

  operation: deploy, destroy

* file_name

  Name of the docker image

* instance_name

  Name of instance

## Contribution
If you find a BUG or have any questions, please ask**issues**

If you want to participate in code development, please submit**Pull Requests**

e.g.：
* Integrate to the additional cloud service provider
* Expansion interface function
* Performance optimization
* And so on...

**We welcome your contributions and hope to make this project better**

## LICENSE
MIT LICENSE
