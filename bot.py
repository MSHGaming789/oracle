displayName = 'instance-20221210-1820'
compartmentId = 'ocid1.tenancy.oc1..aaaaaaaarlv7wpd423matdc6pj7kpaqa4bku2wgfrpwsb7e6cigwq73hkctq'
availabilityDomain = "gHWT:AP-SINGAPORE-1-AD-1"
imageId = "ocid1.image.oc1.ap-singapore-1.aaaaaaaase3dr4tvkg7qn47txxpwpgnxfixukrcp23vnkqzdfra2wuicz4rq"
subnetId = 'ocid1.subnet.oc1.ap-singapore-1.aaaaaaaau3xhuy67jwkgcaggie6yegycy7i5ypdsbrjv63cpuo4ya4bp4mja'
ssh_authorized_keys = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCzJFeF/VlDcDEl2INBkTqjGweuUFLP6M+4CyVwkiQBzNl9VFF7zem5brY6g8hHKqh0bbFhU7BEUOe2T3CQbyi+79uA2caEnQdi75Tf3egqsQxNTCST2xjTHJwi0LZoMXOQadHKscldbP+/NJwedK4QChRW7gIgHR9CAnuWYbxLHAAcq5idJGlhlKL5YcAnSEgFu8sAZGcFuoiWh5VQb7tC+K1DCZk4JQGmCRPrCzYmnaV0FblIijCgnjrryKwrIKuflQ3MCEbb7CxY2rpPGyXtOP68p5KAmPnLw4Ljk39UoZG7MRJvrbpPCmFMp+V7BeGugiXkNg+9uYbN4VOJ8dzHQN9+QHMiTBHjddATvxapb5e2h8nBXo9iCVRX+RGbh/qcEC5AHKVQg3gQYvom5PM3fdDOvyTKeBnhwzcOkSwSCvxTBy1/U00Q6joUL6pvWsWaYoKyZ2gwiwYNDc0HDD0pXiJZgqzwmehC4QWc6KtR0s5y9P3eTmo9R/CuzG4ThAU= sifat@Shofiuls-MacBook-Air.local"

import os
os.system("pip install oci")
os.system("pip install requests")
import oci
import logging
import time
import sys
import requests

LOG_FORMAT = '[%(levelname)s] %(asctime)s - %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler("oci.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

ocpus = 4
memory_in_gbs = 24
wait_s_for_retry = 10

logging.info("#####################################################")
logging.info("Script to spawn VM.Standard.A1.Flex instance")


message = f'Start spawning instance VM.Standard.A1.Flex - {ocpus} ocpus - {memory_in_gbs} GB'
logging.info(message)

logging.info("Loading OCI config")
config = oci.config.from_file(file_location="./config")

logging.info("Initialize service client with default config file")
to_launch_instance = oci.core.ComputeClient(config)


message = f"Instance to create: VM.Standard.A1.Flex - {ocpus} ocpus - {memory_in_gbs} GB"
logging.info(message)

logging.info("Check current instances in account")
logging.info(
    "Note: Free upto 4xVM.Standard.A1.Flex instance, total of 4 ocpus and 24 GB of memory")
current_instance = to_launch_instance.list_instances(
    compartment_id=compartmentId)
response = current_instance.data

total_ocpus = total_memory = _A1_Flex = 0
instance_names = []
if response:
    logging.info(f"{len(response)} instance(s) found!")
    for instance in response:
        logging.info(f"{instance.display_name} - {instance.shape} - {int(instance.shape_config.ocpus)} ocpu(s) - {instance.shape_config.memory_in_gbs} GB(s) | State: {instance.lifecycle_state}")
        instance_names.append(instance.display_name)
        if instance.shape == "VM.Standard.A1.Flex" and instance.lifecycle_state not in ("TERMINATING", "TERMINATED"):
            _A1_Flex += 1
            total_ocpus += int(instance.shape_config.ocpus)
            total_memory += int(instance.shape_config.memory_in_gbs)

    message = f"Current: {_A1_Flex} active VM.Standard.A1.Flex instance(s) (including RUNNING OR STOPPED)"
    logging.info(message)
else:
    logging.info(f"No instance(s) found!")


message = f"Total ocpus: {total_ocpus} - Total memory: {total_memory} (GB) || Free {4-total_ocpus} ocpus - Free memory: {24-total_memory} (GB)"
logging.info(message)

if total_ocpus + ocpus > 4 or total_memory + memory_in_gbs > 24:
    message = "Total maximum resource exceed free tier limit (Over 4 ocpus/24GB total). **SCRIPT STOPPED**"
    logging.critical(message)
    sys.exit()

if displayName in instance_names:
    message = f"Duplicate display name: >>>{displayName}<<< Change this! **SCRIPT STOPPED**"
    logging.critical(message)
    sys.exit()

message = f"Precheck pass! Create new instance VM.Standard.A1.Flex: {ocpus} opus - {memory_in_gbs} GB"
logging.info(message)

instance_detail = oci.core.models.LaunchInstanceDetails(
    metadata={
        "ssh_authorized_keys": ssh_authorized_keys
    },
    availability_domain=availabilityDomain,
    shape='VM.Standard.A1.Flex',
    compartment_id=compartmentId,
    display_name=displayName,
    source_details=oci.core.models.InstanceSourceViaImageDetails(
        source_type="image", image_id=imageId),
    create_vnic_details=oci.core.models.CreateVnicDetails(
        assign_public_ip=False, subnet_id=subnetId, assign_private_dns_record=True),
    agent_config=oci.core.models.LaunchInstanceAgentConfigDetails(
        is_monitoring_disabled=False,
        is_management_disabled=False,
        plugins_config=[oci.core.models.InstanceAgentPluginConfigDetails(
            name='Vulnerability Scanning', desired_state='DISABLED'), oci.core.models.InstanceAgentPluginConfigDetails(name='Compute Instance Monitoring', desired_state='ENABLED'), oci.core.models.InstanceAgentPluginConfigDetails(name='Bastion', desired_state='DISABLED')]
    ),
    defined_tags={},
    freeform_tags={},
    instance_options=oci.core.models.InstanceOptions(
        are_legacy_imds_endpoints_disabled=False),
    availability_config=oci.core.models.LaunchInstanceAvailabilityConfigDetails(
        recovery_action="RESTORE_INSTANCE"),
    shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
        ocpus=ocpus, memory_in_gbs=memory_in_gbs)
)

to_try = 1
while to_try<360:
    try:
        to_launch_instance.launch_instance(instance_detail)
        to_try = False
        message = 'Success! Edit vnic to get public ip address'
        logging.info(message)
        sys.exit()
    except oci.exceptions.ServiceError as e:
        if e.status == 500:
            message = f"{e.message} Retry in {wait_s_for_retry}s"
        else:
            message = f"{e} Retry in {wait_s_for_retry}s"
        logging.info(message)
        time.sleep(wait_s_for_retry)
        to_try=to_try+1
    except Exception as e:
        message = f"{e} Retry in {wait_s_for_retry}s"
        logging.info(message)
        time.sleep(wait_s_for_retry)
        to_try=to_try+1
    except KeyboardInterrupt:
        sys.exit()
