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

#####################################      SCRIPT SETTING, CHANGE THIS        #########################################
ocpus = 4
memory_in_gbs = 24
wait_s_for_retry = 90

# 根据 main.tf 同步
instance_display_name = 'ins****'
compartment_id = 'oci*******'
domain = "**********"
image_id = "oci********"
ssh_key = "ssh**********"

# 【严重注意】：必须确保此 subnet_id 真实存在于你的 OCI 账号中！如果网络还没建，请先去网页端建好网络再复制 OCID 过来。
subnet_id = 'ocid****************'





# Telegram setting
session = requests.Session()
bot_api = '*********'
chat_id = '*********'
######################################################################################################################

def telegram_notify(session, bot_api, chat_id, message):
    '''Notify via telegram'''
    try:
        session.get(f'https://api.telegram.org/bot{bot_api}/sendMessage?chat_id={chat_id}&text={message}')
    except:
        logging.info("Message fail to sent via telegram")

logging.info("#####################################################")
logging.info("Script to spawn VM.Standard.A1.Flex instance")

message = f'Start spawning instance VM.Standard.A1.Flex - {ocpus} ocpus - {memory_in_gbs} GB'
logging.info(message)
telegram_notify(session, bot_api, chat_id, message)

logging.info("Loading OCI config")
config = oci.config.from_file(file_location="./config")

logging.info("Initialize service client with default config file")
to_launch_instance = oci.core.ComputeClient(config)

message = f"Instance to create: VM.Standard.A1.Flex - {ocpus} ocpus - {memory_in_gbs} GB"
logging.info(message)
telegram_notify(session, bot_api, chat_id, message)

logging.info("Check current instances in account")
current_instance = to_launch_instance.list_instances(compartment_id=compartment_id)
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

    message = f"Current: {_A1_Flex} active VM.Standard.A1.Flex instance(s)"
    logging.info(message)
else:
    logging.info(f"No instance(s) found!")

message = f"Total ocpus: {total_ocpus} - Total memory: {total_memory} (GB) || Free {4-total_ocpus} ocpus - Free memory: {24-total_memory} (GB)"
logging.info(message)

if total_ocpus + ocpus > 4 or total_memory + memory_in_gbs > 24:
    message = "Total maximum resource exceed free tier limit (Over 4 ocpus/24GB total). **SCRIPT STOPPED**"
    logging.critical(message)
    sys.exit()

if instance_display_name in instance_names:
    message = f"Duplicate display name: >>>{instance_display_name}<<< Change this! **SCRIPT STOPPED**"
    logging.critical(message)
    sys.exit()

# Instance-detail 构建
instance_detail = oci.core.models.LaunchInstanceDetails(
    metadata={
        "ssh_authorized_keys": ssh_key
    },
    availability_domain=domain,
    shape='VM.Standard.A1.Flex',
    compartment_id=compartment_id,
    display_name=instance_display_name,
    source_details=oci.core.models.InstanceSourceViaImageDetails(
        source_type="image",
        image_id=image_id,
        boot_volume_size_in_gbs=150
    ),
    create_vnic_details=oci.core.models.CreateVnicDetails(
        assign_public_ip=False,
        subnet_id=subnet_id,
        assign_private_dns_record=True
    ),
    agent_config=oci.core.models.LaunchInstanceAgentConfigDetails(
        is_monitoring_disabled=False,
        is_management_disabled=False,
        plugins_config=[
            oci.core.models.InstanceAgentPluginConfigDetails(name='Vulnerability Scanning', desired_state='DISABLED'),
            oci.core.models.InstanceAgentPluginConfigDetails(name='Compute Instance Monitoring', desired_state='ENABLED'),
            oci.core.models.InstanceAgentPluginConfigDetails(name='Bastion', desired_state='DISABLED')
        ]
    ),
    defined_tags={},
    freeform_tags={},
    instance_options=oci.core.models.InstanceOptions(
        are_legacy_imds_endpoints_disabled=True
    ),
    availability_config=oci.core.models.LaunchInstanceAvailabilityConfigDetails(
        recovery_action="RESTORE_INSTANCE"
    ),
    shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
        ocpus=ocpus, memory_in_gbs=memory_in_gbs
    )
)

# 核心抢机循环
to_try = True
while to_try:
    try:
        to_launch_instance.launch_instance(instance_detail)
        to_try = False
        message = 'Success! Instance spawned successfully.'
        logging.info(message)
        telegram_notify(session, bot_api, chat_id, message)
        session.close()
    except oci.exceptions.ServiceError as e:
        if e.status == 500:
            message = f"{e.message} Retry in {wait_s_for_retry}s"
            #telegram_notify(session, bot_api, chat_id, message) #可选,没抢到服务器也发送通知
        else:
            message = f"{e} Retry in {wait_s_for_retry}s"
            # 仅在非 500 错误时通知（如 404 找不到资源，401 权限错误）
            telegram_notify(session, bot_api, chat_id, message)
        logging.info(message)
        time.sleep(wait_s_for_retry)
    except Exception as e:
        message = f"{e} Retry in {wait_s_for_retry}s"
        logging.info(message)
        telegram_notify(session, bot_api, chat_id, message)
        time.sleep(wait_s_for_retry)
    except KeyboardInterrupt:
        session.close()
        sys.exit()