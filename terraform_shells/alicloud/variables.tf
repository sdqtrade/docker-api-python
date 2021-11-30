variable "access_key" {
    default = ""
}
variable "secret_key" {
    default = ""
}
variable "client_name"{
    default = ""
}
variable "docker_registry_url" {
    default = ""
}
variable "docker_registry_username" {
    default = ""
}
variable "docker_registry_password" {
    default = ""
}
variable "region" {
    default = "cn-chengdu"
}

variable "vpc_id" {
    default = "vpc-2vcsxi2elu1bajzujj78i"
}
variable "vswitch_id" {
    default = "vsw-2vcveik9n5xqwcpxva7q2"
}


variable "private_ip" {
    default = "192.168.0.60"
}


variable "number" {
    default = "1"
}

variable "count_format" {
    default = "%02d"
}

variable "image_id" {
    default = "centos_7_7_x64_20G_alibase_20200329.vhd"
    }

variable "role" {
    default = "prod"
}


variable "short_name" {
    default = "quant"
}

variable "ecs_type" {
    default = "ecs.c5"
}

variable "ecs_password" {
    default = "test"
}

variable "internet_charge_type" {
    default = "PayByTraffic"
}

variable "internet_max_bandwidth_out" {
    default = 100
}

variable "disk_category" {
    default = "cloud_ssd"
}

variable "disk_size" {
    default = "100"
}

variable "nic_type" {
    default = "intranet"
}
variable "ssh_key_public" {
    default     = "~/.ssh/id_rsa.pub"
    description = "Path to the SSH public key for accessing cloud instances. Used for creating AWS keypair."
}

variable "ssh_key_private" {
    default     = "~/.ssh/id_rsa"
    description = "Path to the SSH public key for accessing cloud instances. Used for creating AWS keypair."
}

variable "file_name" {
    default = ""
}

variable "instance_name" {
    default = ""
}
