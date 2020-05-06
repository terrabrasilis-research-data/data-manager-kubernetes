#!flask/bin/python
from flask_httpauth import HTTPBasicAuth
from kubernetes import client, config
from flask import Flask, jsonify
from flask import make_response
from flask_cors import CORS
from yaml import load, dump
from flask import request
from flask import url_for
import yaml
import os 

# env
def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = "Expected environment variable '{}' not set.".format(name)
        raise Exception(message)

# values
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_FOLDER = os.path.join(APP_ROOT, 'static')
    
# app
app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# errorhandler
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

#+--------------------------------------------------------+
#| read()                                                 |
#+--------------------------------------------------------+
@app.route('/api/v1.0/read', methods=['GET'])
def read_pods():
        
    # Configs can be set in Configuration class directly or using helper utility
    config.load_kube_config()
    
    # kubernetes api
    v1 = client.CoreV1Api()
    
    # list pods
    pod_list = v1.list_namespaced_pod("default")
    pod_list_json = []
    
    # read pods
    for pod in pod_list.items:
        pod_list_json.append({"name": pod.metadata.name,
                              "status": pod.status.phase,
                              "ip": pod.status.pod_ip})
    
    # return
    return jsonify(pod_list_json)

#+--------------------------------------------------------+
#| create()                                               |
#+--------------------------------------------------------+
@app.route('/api/v1.0/create', methods=['GET'])
def create_repository():

    #yaml_folders = ['geonetwork', 'geoserver', 'nginx', 'owncloud', 'postgis', 'terrama2', 'volume']
    yaml_folders = ['geonetwork', 'postgis']

    # open folders
    for folder in yaml_folders:
        
        # list the yamls
        yamls_list = os.listdir(os.path.join(STATIC_FOLDER, folder))
        yamls_list = [k for k in yamls_list if '.yaml' in k]

        # open each yaml
        for yamls_item in yamls_list:
            
            # debug
            #print(yamls_item)
            
            # open yaml files
            with open(os.path.join(STATIC_FOLDER, folder, yamls_item)) as file:
                
                # debug
                #print(current_yaml)

                # load yaml
                dep = yaml.safe_load(file)

                # kubernetes api
                k8s_beta = client.ExtensionsV1beta1Api()
                
                # create namespace and deploy yaml
                resp = k8s_beta.create_namespaced_deployment(body=dep, namespace="default")
                
                # Print result
                print("Deployment created. status='%s'" % str(resp.status))

    # return
    return jsonify({"result":"sucess"})

if __name__ == '__main__':
    app.run(get_env_variable("HOST_IP"), debug=True, port=8070)
