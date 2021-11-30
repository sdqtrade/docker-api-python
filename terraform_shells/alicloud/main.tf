provider "alicloud" {
    access_key = var.access_key
    secret_key = var.secret_key
    region     = var.region
    #version    = "~> 1.5.0"
}

data "alicloud_instance_types" "instance_type" {
    instance_type_family = var.ecs_type
    cpu_core_count       = "2"
    memory_size          = "4"
}

# Generate a random vm name
resource "random_string" "keypair-name" {
  length  = 8
  upper   = false
  number  = false
  lower   = true
  special = false
}

resource "alicloud_security_group" "group" {
    name        =  "${var.short_name}-${var.role}"
    description = "New security group"
    vpc_id      =  var.vpc_id
}

resource "alicloud_key_pair" "alicloud_key_pair" {
    key_pair_name   = "${var.short_name}-${var.role}-${random_string.keypair-name.result}"
    public_key      = "${file(var.ssh_key_public)}"
}



data "alicloud_zones" "zones_ds" {
    available_instance_type = data.alicloud_instance_types.instance_type.instance_types[0].id
}


resource "alicloud_instance" "instance" {
    #instance_name   = "${var.short_name}-${var.role}-${format(var.count_format, count.index + 1)}"
    instance_name   = "${var.instance_name}"
    host_name       = "${var.short_name}-${var.role}-${format(var.count_format, count.index + 1)}"
    image_id        = var.image_id
    instance_type   = data.alicloud_instance_types.instance_type.instance_types[0].id
    count           = var.number
    security_groups = alicloud_security_group.group.*.id
    vswitch_id      = var.vswitch_id
    #private_ip      = var.private_ip
    
    internet_charge_type       = var.internet_charge_type
    internet_max_bandwidth_out = var.internet_max_bandwidth_out
    
    password = var.ecs_password
    
    instance_charge_type          = "PostPaid"
    system_disk_category          = "cloud_efficiency"
    security_enhancement_strategy = "Deactive"
    key_name = alicloud_key_pair.alicloud_key_pair.key_pair_name
    system_disk_size              = var.disk_size  
    connection {
        host = "${self.public_ip}"
        type        = "ssh"
        user        = "root"
        private_key = "${file(var.ssh_key_private)}"
    }

    provisioner "remote-exec" {
        # Install Python for Ansible
        inline = ["yum install docker -y;systemctl enable docker;systemctl start docker;"]
    }

   # provisioner "local-exec" {
   #      command = "ansible-playbook -u root -i myinventory --private-key ${var.ssh_key_private} -T 300 provision.yml"
   #}
    
   # data_disks {
   #    name        = "disk1"
   #        size        = "200"
   #        category    = "cloud_efficiency"
   #        description = "disk1"
   #}
    tags = {
        role = var.role
    }
}


data "alicloud_instances" "instances_ds" {
  #count  = var.number

  name_regex = "${var.short_name}-${var.role}-${format(var.count_format, 1)}"
  status = "Running"
}
resource "null_resource" "install_docker" {
         depends_on = [alicloud_instance.instance]
          triggers = {
              key = "${uuid()}"
          }
         connection {
              type        = "ssh"
              host        = alicloud_instance.instance.*.public_ip[0] 
              port        = "22"
              private_key = "${file("~/.ssh/id_rsa")}"
        }
        provisioner "local-exec" {
              command    = "rm -rf ${var.file_name}.tar; docker save -o  ${var.file_name}.tar  ${var.docker_registry_url}/${var.client_name};"
           }
        provisioner "file" {
           source      = "${var.file_name}.tar"
           destination = "/root/${var.file_name}.tar"
        }  
         provisioner "remote-exec" {
           inline = ["docker stop ${var.file_name};docker rm -f ${var.file_name};docker image rm ${var.docker_registry_url}/${var.client_name};docker load </root/${var.file_name}.tar;docker run -d --name ${var.file_name} -p 80:80 ${var.docker_registry_url}/${var.client_name};"]
        }
}
