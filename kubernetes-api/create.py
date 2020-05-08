from kubernetes.client.rest import ApiException
from kubernetes import client, config
from yaml import load, dump
from flask import request
from flask import url_for
from os import path
import yaml
import os 

#yaml_folders = ['geonetwork', 'geoserver', 'nginx', 'owncloud', 'postgis', 'terrama2', 'volume']
yaml_folders = ['geonetwork']

# values
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_FOLDER = os.path.join(APP_ROOT, 'static')

# open folders
for folder in yaml_folders:
    
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    config.load_kube_config()

    # list the yamls
    yamls_list = os.listdir(os.path.join(STATIC_FOLDER, folder))
    yamls_list = [k for k in yamls_list if '-deployment.yaml' in k]

    # open each yaml
    for yamls_item in yamls_list:
        
        # debug
        print(yamls_item)
        
        # open yaml files
        with open(path.join(STATIC_FOLDER, folder, yamls_item)) as f:
                
            # load yaml    
            dep = yaml.load(f)
            
            # kubernetes api
            k8s_beta = client.ExtensionsV1beta1Api()
            
            # create namespace and deploy yaml
            resp = k8s_beta.create_namespaced_deployment(
                body=dep, namespace="default")
            print("Deployment created. status='%s'" % str(resp.status))
