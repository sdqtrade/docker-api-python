resource "alicloud_security_group_rule" "allow_80" {
    type              = "ingress"
    ip_protocol       = "tcp"
    nic_type          = var.nic_type
    policy            = "accept"
    port_range        = "80/80"
    priority          = 1
    security_group_id = alicloud_security_group.group.id
    #TO BE MODIFIED
    cidr_ip           = "192.168.0.0/16"
}

resource "alicloud_security_group_rule" "allow_22_1" {
    type              = "ingress"
    ip_protocol       = "tcp"
    nic_type          = var.nic_type
    policy            = "accept"
    port_range        = "22/22"
    priority          = 1
    security_group_id = alicloud_security_group.group.id
    #TO BE MODIFIED
    cidr_ip           = "0.0.0.0/32"
}



