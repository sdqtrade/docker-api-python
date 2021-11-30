# _*_ coding: utf-8 _*_
import random
import tornado.ioloop
import tornado.web
import urllib3
import docker
import os
import json
from shutil import copyfile
import threading
import string
import subprocess
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')  # logging.basicConfig函数对日志的输出格式及方式做相关配置

client = docker.from_env()
_http = urllib3.PoolManager()

# 当前系统支持的云厂商
PROVIDERS = ['alicloud']

# docker配置文件保存路径
PATH = '/docker-files/{}'

# SDK wheel包存放路径
API_APP_PATH = '/python-api/whl/apps/{}'

# SDK 需要的配置文件名称
USER_SETTING_NAME = 'b2953074-cfe7-11eb-b839-3ca067558dd7.json'
SYSTEM_SETTING_NAME = 'c281efb2-cfe7-11eb-ada6-3ca067558dd7.json'

# 不同的交易平台，对应的配置文件名称对照表
API_PLATFORM_SETTING_NAME = {
    '1001': 'FutuOpenD.xml',
    'zvsts': 'config.xml'
}

# 默认的启动端口
SERVER_PORT = 6787

# 不同的交易平台，在启动策略容器时，需要优先执行的命令列表
CONTAINER_STARTUP_SHELLS = {
    'zvsts': [
        '/app/api/run.sh start'
    ]
}

# docker registry相关配置
# 请注意：registry.self.com为虚拟域名，无法外部访问
DOCKER_REGISTRY_URL = 'registry.self.com:9443'
DOCKER_REGISTRY_USER = 'docker'
DOCKER_REGISTRY_PASSWORD = 'test'

# terraform的两种操作名称
TERRAFORM_DEPLOY_ACTION = 'deploy'
TERRAFORM_DESTROY_ACTION = 'destroy'

class StopContainerHandler(tornado.web.RequestHandler):
    """
    容器（环境）销毁Handler
    """
    def post(self):
        """
        执行销毁操作，参数：

        tag -> 容器名称

        u -> 容器ID（与创建时一致）

        provider -> 云厂商名称

        api_key,api_secret_key -> API密钥

        firm_name -> 实例名称
        """
        data = tornado.escape.json_decode(self.request.body)
        tag = data.get('tag')
        u = data.get('u')
        provider = data.get('provider')
        api_key = data.get('api_key')
        api_secret_key = data.get('api_secret_key')
        instance_name = data.get('firm_name')

        try:
            logging.info('准备destroy操作，tag -> %s' % tag)
            dir_path = PATH.format(u)
            shell_dir = dir_path + '/terraform-shells'
            os.chdir(shell_dir)
            shell = 'sh deploy.sh %s %s %s %s %s %s %s %s %s %s' % (
                DOCKER_REGISTRY_URL,
                DOCKER_REGISTRY_USER,
                DOCKER_REGISTRY_PASSWORD,
                tag,
                provider,
                api_key,
                api_secret_key,
                TERRAFORM_DESTROY_ACTION,
                'destroy_file',
                instance_name
            )
            process = subprocess.Popen(shell, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (stdout, stderr) = process.communicate()
            exit_code = process.returncode

            ret = {
                'code': exit_code
            }
            logging.info('容器已删除，容器ID -> {}'.format(tag))
        except Exception as e:
            ret = {
                'code': -1
            }
            logging.info('容器删除时报错，可能不存在，容器ID -> {}'.format(tag))
        self.write(json.dumps(ret))


class ApiHandler(tornado.web.RequestHandler):
    """
    API Handler
    """
    def post(self):
        """
        异步创建环境，参数：

        provider -> 云厂商名称

        u -> 唯一标识

        pyFile -> 策略文件内容

        user_settings -> 用户配置文件内容

        system_settings -> 系统配置文件内容

        api_settings -> 交易平台配置内容

        ap_name -> 交易平台名称

        containerId -> 容器ID
        
        api_key,api_secret_key -> API密钥

        firm_name -> 实例名称
        """
        data = tornado.escape.json_decode(self.request.body)
        provider = data.get('provider')
        u = data.get('u')
        if provider not in PROVIDERS:
            ret = {
                'code': 2,
                'msg': '%s provider not support yet' % provider
            }
            self.write(json.dumps(ret))
            return
        file_name = random_file_name()
        tag = 'strategy/%s:latest' % (u)
        threading.Thread(target=create_service, args=(data, file_name, tag)).start()
        ret = {
            'code': 0,
            'tag': tag
        }
        self.write(json.dumps(ret))
        
def create_service(data, file_name, tag):
    """
    根据传入参数，构建策略环境，执行流程如下：
    
    1. 根据传入参数，生成必要文件，如：Dockerfile,策略python文件等

    2.通过不同厂商的docker容器，打包可执行文件

    3.将可执行文件打包到最终的策略容器，并将此镜像上传到docker registry

    4.调用terraform进行远程部署

    5.等待最终结果，并将结果通知到主服务
    """
    pyFileContent = data.get('pyFile')
    userSettingsContent = data.get('user_settings')
    systemSettingsContent = data.get('system_settings')
    u = data.get('u')
    apiSettingsContent = data.get('api_settings')
    api_platform_name = data.get('ap_name')
    containerId = data.get('containerId')
    provider = data.get('provider')
    api_key = data.get('api_key')
    api_secret_key = data.get('api_secret_key')
    instance_name = data.get('firm_name')

    try:
        dirPath = PATH.format(u)
        os.makedirs(dirPath)

        # 写入python文件，配置文件
        logging.info('准备写入python及配置文件')
        pyFile = dirPath + '/{}'.format(file_name + '.py')
        f = open(pyFile, 'w+', encoding="utf-8")
        f.write(pyFileContent)
        f.close()

        userSttings = dirPath + '/' + USER_SETTING_NAME
        f = open(userSttings, 'w+', encoding="utf-8")
        f.write(userSettingsContent)
        f.close()

        systemSettings = dirPath + '/' + SYSTEM_SETTING_NAME
        f = open(systemSettings, 'w+', encoding="utf-8")
        f.write(systemSettingsContent)
        f.close()
        logging.info('写入python及配置文件完成')

        logging.info('准备调用API容器，生成二进制可执行文件，当前平台 -> %s' % api_platform_name)
        shell_content = '#!/bin/bash\n\
    pyinstaller %s.py\n\
    cp ./b2953074-cfe7-11eb-b839-3ca067558dd7.json ./c281efb2-cfe7-11eb-ada6-3ca067558dd7.json ./dist/%s\n\
    cp -R ./api ./dist/%s\n' % (file_name, file_name, file_name)
        # if api_platform_name == '1001':
        shell_content += 'mkdir -p ./dist/%s/futu/common\n\
    cp -R /usr/local/lib/python3.8/site-packages/futu/common/pb ./dist/%s/futu/common/\n\
    cp /usr/local/lib/python3.8/site-packages/futu/VERSION.txt ./dist/%s/futu' % (file_name, file_name, file_name)
        converter_shell = dirPath + '/run.sh'
        f = open(converter_shell, 'w+', encoding="utf-8")
        f.write(shell_content)
        f.close()

        app_script = ''
        api_path = API_APP_PATH.format(api_platform_name)
        if os.path.exists(api_path):
            app_script = 'chmod +x /app/api/* && '
            appPath = dirPath + '/api'
            os.makedirs(appPath)
            for root, dirs, files in os.walk(api_path):
                for file in files:
                    src_file = os.path.join(root, file)
                    copyfile(src_file, os.path.join(appPath, file))

            if api_platform_name in API_PLATFORM_SETTING_NAME:
                setting_file_name = API_PLATFORM_SETTING_NAME[api_platform_name]
                apiSettings = dirPath + '/api/' + setting_file_name
                f = open(apiSettings, 'w+', encoding="utf-8")
                f.write(apiSettingsContent)
                f.close()

        # 准备调用API容器，生成二进制可执行文件
        volumes = '/home/go%s:/work' % dirPath
        logging.info('volumes -> %s' % volumes)
        client.containers.run('api/%s' % api_platform_name,
            command='sh run.sh',
            remove=True,
            detach=False,
            privileged=True,
            volumes=[volumes])
        logging.info('生成二进制可执行文件操作已完成，当前平台 -> %s' % api_platform_name)

        logging.info('准备生成最终的策略容器')
        # 准备生成最终的策略容器
        python_shell = '/app/' + file_name
        if api_platform_name in CONTAINER_STARTUP_SHELLS:
            python_shell = '{} && '.format(' && '.join(CONTAINER_STARTUP_SHELLS[api_platform_name])) + python_shell

        dockerfileContetn = 'FROM ubuntu\n\
    ADD ./dist/%s /app\n\
    ENV LANG=C.UTF-8\n\
    RUN %s export DEBIAN_FRONTEND=noninteractive \\\n\
    && apt-get update \\\n\
    && apt-get install -y tzdata \\\n\
    && ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \\\n\
    && dpkg-reconfigure --frontend noninteractive tzdata\n\
    WORKDIR /app\n\
    CMD %s' % (file_name, app_script, python_shell)

        dockerFile = dirPath + '/Dockerfile'
        f = open(dockerFile, 'w+', encoding="utf-8")
        f.write(dockerfileContetn)
        f.close()

        final_tag = '%s/%s' % (DOCKER_REGISTRY_URL, tag)
        logging.info('final_tag -> %s' % final_tag)
        client.images.build(path=dirPath, tag=final_tag)
        logging.info('生成最终的策略容器操作已完成，tag -> %s' % final_tag)

        logging.info('准备调用terraform shell进行远程部署')
        # 准备调用terraform进行远程部署
        # copy shell
        shell_dir = dirPath + '/terraform-shells'
        os.makedirs(shell_dir)
        for root, dirs, files in os.walk('/terraform-shells'):
                for file in files:
                    src_file = os.path.join(root, file)
                    copyfile(src_file, os.path.join(shell_dir, file))
        shell = 'sh deploy.sh %s %s %s %s %s %s %s %s %s %s' % (
            DOCKER_REGISTRY_URL,
            DOCKER_REGISTRY_USER,
            DOCKER_REGISTRY_PASSWORD,
            tag,
            provider,
            api_key,
            api_secret_key,
            TERRAFORM_DEPLOY_ACTION,
            file_name,
            instance_name
        )
        os.chdir(shell_dir)
        logging.info('changing work dir -> %s' % shell_dir)
        logging.info('terraform shell -> %s' % shell)
        process = subprocess.Popen(shell, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = process.communicate()
        exit_code = process.returncode
        logging.info('terraform shell调用已完成，exit code -> %s' % exit_code)
        if exit_code != 0:
            result = {'id': containerId, 'state': 6, 'msg': 'terraform shell调用失败，exit code -> %s' % exit_code}
            _http.request(
                'POST',
                'http://strategy-service:6070/container-info/container_state',
                body=json.dumps(result).encode('utf-8'),
                headers={'Content-Type': 'application/json;charset=utf-8'}
            )
            return

        logging.info('容器已创建，容器ID -> {}'.format(tag))
    except Exception:
        logging.exception('create service过程中发生异常，id -> %s' % u)
        result = {'id': containerId, 'state': 6, 'msg': '未知错误，请查看日志'}
        _http.request(
            'POST',
            'http://strategy-service:6070/container-info/container_state',
            body=json.dumps(result).encode('utf-8'),
            headers={'Content-Type': 'application/json;charset=utf-8'}
        )

def make_app():
    return tornado.web.Application([
        (r"/api", ApiHandler),
        (r"/api/containers/stop", StopContainerHandler)
    ])

def random_file_name():
    return  ''.join(random.sample(string.ascii_letters + string.digits, 8))

if __name__ == "__main__":
    app = make_app()
    app.listen(SERVER_PORT)
    logging.info('server started on port {}'.format(SERVER_PORT))
    tornado.ioloop.IOLoop.current().start()
