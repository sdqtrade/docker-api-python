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
echo "docker_registry_url=$docker_registry_url";
echo "docker_registry_username=$docker_registry_username";
echo "docker_registry_password=$docker_registry_password";
echo "client_name=$client_name";
echo "client_cloud=$client_cloud";
echo "access_key=$access_key";
echo "secret_key=$secret_key";
echo "deploy_action=$deploy_action";
echo "file_name=$file_name";
echo "instance_name=$instance_name";
if [ "$deploy_action" = "deploy" ]; then
    terraform apply  -auto-approve -var="docker_registry_username=$docker_registry_username"  -var="docker_registry_password=$docker_registry_password" -var="access_key=$access_key" -var="secret_key=$secret_key" -var="docker_registry_url=$docker_registry_url" -var="client_name=$client_name" -var="file_name=$file_name" -var="instance_name=$instance_name";

    if [ $? -ne 1 ]; then
      echo "successfully to apply terraform";
    else
      echo "failed to apply trraform";
      exit 1;
    fi
else
    terraform destroy -auto-approve -var="docker_registry_username=$docker_registry_username"  -var="docker_registry_password=$docker_registry_password"  -var="access_key=$access_key" -var="secret_key=$secret_key" -var="docker_registry_url=$docker_registry_url"  -var="client_name=$client_name" -var="file_name=$file_name" -var="instance_name=$instance_name";

    if [ $? -ne 1 ]; then
      echo "successfully to destroy terraform";
    else
      echo "failed to destroy trraform";
      exit 1;
    fi
fi
