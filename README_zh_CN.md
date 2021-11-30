<p align="center">
    <a href="http://www.sdqtrade.com/">
        <img alt="蓝色量化交易平台" src="logo.png" width="150" style="max-width: 100%" />
    </a>
</p>
<p align="center">
    <a href="https://opensource.org/licenses/MIT">
        <img src="https://img.shields.io/badge/license-MIT-green" />
    </a>
</p>
<h1 align="center">蓝色量化交易平台Docker API</h1>

## **Looking for English version?[click here](./README.md)**
## 介绍
本repo属于蓝色量化交易平台的一部分，主要职责为打包策略文件、构建镜像、推送到指定环境等。

此API采用python编写，以http api的方式提供内部服务。

职责如下：
* 打包策略文件（python）
* 构建docker镜像
* 推送镜像并执行策略容器
* 容器、环境销毁

  使用terraform对接不同云服务提供商API，以实现自动的云服务器购买、配置参数、容器上传、启动等。

目前支持的云服务提供商：
* 阿里云
* *AWS（正在开发中）*
* *敬请期待...*

## 快速开始
### 1.安装pip依赖
```bash
pip install -r requirements.txt
```
### 2.[安装docker](https://docs.docker.com/get-docker/)
### 3.[安装terraform](https://www.terraform.io/downloads.html)

### 4.启动服务
```python
python app.py
```
### 请求接口
* POST http://localhost:6787/api

  根据传入参数（策略内容、容器属性、配置文件、云服务提供商凭证等），构建容器并推送到指定的云服务提供商处理

* POST http://localhost:6787/api/containers/stop

  销毁指定容器或环境

## terraform说明
### 目录结构
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
* terraform_shells存放不同云服务提供商的API对接文件
* 以文件夹名称区分不同的云服务厂商
* 全部使用terraform编写
* shell的调用均使用deploy.sh做为入口

### deploy.sh入口参数
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

  docker registry的URL、用户名、密码

* client_name

  docker image名称

* client_cloud

  云服务商名称

* access_key
* secret_key

  API密钥

* deploy_action

  执行操作，deploy -> 部署，destroy -> 销毁

* file_name

  docker image打包时的文件名

* instance_name

  实例名称

## 如何贡献
如果您发现了BUG或者有任何疑问，欢迎提出**issues**

如果您想参与到代码开发，欢迎提交**Pull Requests**

例如：
* 对接新的云服务提供商
* 扩充接口功能
* 性能优化
* And so on...

**我们非常欢迎您的贡献，希望可以让此项目变得更好**

## LICENSE
MIT LICENSE