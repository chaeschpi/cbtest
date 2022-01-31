from common.methods import set_progress
from azure.mgmt.resource import SubscriptionClient
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
import logging
import json


def create_credential_obj(groupObj):
    parameter2 = groupObj.az_tenantId
    parameter3 = groupObj.az_sp
    parameter4 = groupObj.az_sp_secret
    credential_obj = ServicePrincipalCredentials(tenant=parameter2, client_id=parameter3, secret=parameter4)
    return credential_obj

def generate_options_for_subscription(group, control_value=None, **kwargs):
    obj_credential = create_credential_obj(group)
    subscription_client = SubscriptionClient(obj_credential)
    raw = subscription_client.subscriptions.list()
    entry = [] 
    for i in raw: 
        repared_dict = json.dumps({'az_tenantId': group.az_tenantId,
                                    'az_sp': group.az_sp,
                                    'az_sp_secret': group.az_sp_secret,
                                    'subscriptionId': i.subscription_id})
        entry.append((repared_dict,i.display_name))
    
    return  entry
    
def generate_options_for_location(control_value=None, **kwargs):   
    if control_value is None: 
        return []
    if control_value == "":
        return []
        
    dict_obj = json.loads(control_value)
    credential = ServicePrincipalCredentials(tenant=dict_obj['az_tenantId'], client_id=dict_obj['az_sp'], secret=dict_obj['az_sp_secret'])
    subscription_id = dict_obj['subscriptionId']
    subscription_client = SubscriptionClient(credential)
    raw =  subscription_client.subscriptions.list_locations(subscription_id)
 
    entry = [] 
    for i in raw: 
        entry.append((i.name,i.display_name))
        
    return  entry
    


def run(job,group, *args, **kwargs):
    resource = kwargs.get('resource')
    logging.info(kwargs)
    
    location = '{{location}}'
    subscription_obj = json.loads('{{ subscription }}')
    logging.info(subscription_obj)
    subscription = subscription_obj['subscriptionId']
    credential = ServicePrincipalCredentials(tenant=subscription_obj['az_tenantId'], client_id=subscription_obj['az_sp'], secret=subscription_obj['az_sp_secret'])  
    rg_name= '{{ azure_resource_group_name }}'
    
    epcf_serviceGroup = '{{EPCF_service_group}}'
    epcf_description = '{{EPCF_description}}'
    
    if (not epcf_serviceGroup):
        epcf_serviceGroup = "none"
    
    if (not epcf_description):
        epcf_description = "none"
    resource_client = ResourceManagementClient(credential, subscription)
    
    resource_group_params = {'location':location}
    resource_group_params.update(tags={ 'EPCF_Monitoring':'base','EPCF_Managed':'true', 'EPCF_ServiceGroup':epcf_serviceGroup, 'EPCF_Description':epcf_description, 'EPCF_Deploy_Engine' : 'Cloudbolt_CMP', 'EPCF_JobId' : job })
    resource_client.resource_groups.create_or_update(rg_name, resource_group_params)
    
    if True:
        return "SUCCESS", "SQL Service is created!  Go to the Azure Portal for more information", ""
       
        
    else:
        return "FAILURE", "Deployment Faild! ", "For Details go to the Azure Portal"