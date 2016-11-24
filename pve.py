
import sys
from fabric.api import *


""" Configurations """


template = {
    'vm_id': 200,
    'key_file': '/root/ssh/id_rsa'
}

env.hosts = ['128.112.168.28']
env.user = 'root'
env.password = 'PrincetonP4OVS3'


""" Basic PVE Commands"""


def ssh_run(vm_id, command):
    run("ssh -i %s -o 'StrictHostKeyChecking no' mshahbaz@10.10.10.%s \"%s\""
        % (template['key_file'], vm_id, command))


def clone_vm(vm_id, vm_name):
    run("pvesh create /nodes/mshahbaz-poweredge-3-pve/qemu/%s/clone -newid %s -name %s" % (template['vm_id'], vm_id, vm_name))


def start_vm(vm_id):
    run("pvesh create /nodes/mshahbaz-poweredge-3-pve/qemu/%s/status/start" % (vm_id,))


def start_vms(*vm_ids):
    for vm_id in vm_ids:
        start_vm(vm_id)


def stop_vm(vm_id):
    run("pvesh create /nodes/mshahbaz-poweredge-3-pve/qemu/%s/status/stop" % (vm_id,))


def stop_vms(*vm_ids):
    for vm_id in vm_ids:
        stop_vm(vm_id)


def delete_vm(vm_id):
    if vm_id == str(template['vm_id']):
        sys.stderr.write("Error: cannot delete a VM template (vm_id:%s).\n" %(vm_id,))
        sys.exit(1)
    run("pvesh delete /nodes/mshahbaz-poweredge-3-pve/qemu/%s" % (vm_id,))


def delete_vms(*vm_ids):
    for vm_id in vm_ids:
        delete_vm(vm_id)


def reboot_vm(vm_id):
    stop_vm(vm_id)
    start_vm(vm_id)


def sync_vm(vm_id):
    ssh_run(vm_id, 'sync')


def is_vm_ready(vm_id):
    run("ssh -i %s -o 'StrictHostKeyChecking no' mshahbaz@10.10.10.%s 'date'; "
        "while test $? -gt 0; do "
        "  sleep 5; echo 'Trying again ...'; "
        "  ssh -i %s -o 'StrictHostKeyChecking no' mshahbaz@10.10.10.%s 'date'; "
        "done" % (template['key_file'], vm_id,
                  template['key_file'], vm_id))


def configure_vm_network(old_vm_id, vm_id):
    ssh_run(old_vm_id,
            "sudo sed -i 's/address 10.10.10.%s/address 10.10.10.%s/g' /etc/network/interfaces; "
            "sudo sed -i 's/ubuntu-14/ubuntu-14-%s/g' /etc/hostname; "
            "sudo sed -i 's/10.10.10.%s/10.10.10.%s/g' /etc/hosts; "
            "sudo sed -i 's/ubuntu-14/ubuntu-14-%s/g' /etc/hosts"
            % (old_vm_id, vm_id,
               vm_id,
               old_vm_id, vm_id,
               vm_id))


def generate_vm(vm_id, vm_name):
    clone_vm(vm_id, vm_name)
    start_vm(vm_id)
    is_vm_ready(template["vm_id"])
    configure_vm_network(template['vm_id'], vm_id)
    sync_vm(template["vm_id"])
    reboot_vm(vm_id)


def generate_vms(prefix, *vm_ids):
    for vm_id in vm_ids:
        generate_vm(vm_id, '%s-%s' %(prefix, vm_id))


def destroy_vm(vm_id):
    stop_vm(vm_id)
    delete_vm(vm_id)


def destroy_vms(*vm_ids):
    for vm_id in vm_ids:
        destroy_vm(vm_id)


def add_host(vm_id, host_vm_id, host_vm_name):
    ssh_run(vm_id, "echo '10.10.10.%s %s' | sudo tee -a /etc/hosts"
            % (host_vm_id, host_vm_name))