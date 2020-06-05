#!flask/bin/python
from kubernetes.client.rest import ApiException
from flask_httpauth import HTTPBasicAuth
from kubernetes import client, config
from flask import Flask, jsonify
from flask import make_response
from flask_cors import CORS
from yaml import load, dump
from flask import request
from flask import url_for
from flask import abort
import subprocess
import yaml
import os 
import re

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
cors = CORS(app)

# errorhandler
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

#+--------------------------------------------------------+
#| read()                                                 |
#+--------------------------------------------------------+
@app.route('/api/v1.0/read', methods=['PUT'])
def read_pods():    
            
    #  {
    #      "namespace": "gabriel",
    #  }

    if not request.json or not 'namespace' in request.json:
        abort(400)
    
    namespace=request.json['namespace']
            
    pattern = '[a-z0-9]([-a-z0-9]*[a-z0-9])'
    result = re.match(pattern, namespace)

    if not result:
        abort(400)

    # Configs can be set in Configuration class directly or using helper utility
    config.load_kube_config()
    
    # kubernetes api
    v1 = client.CoreV1Api()
    
    # list pods
    pod_list = v1.list_namespaced_pod(namespace)
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
@app.route('/api/v1.0/create', methods=['PUT'])
def create_repository():
    
    #  {
    #      "namespace": "gabriel",
    #      "services": ["geoserver", "nginx", "postgis", "volume"]
    #  }
        
    if not request.json or not 'namespace' and 'services' in request.json:
        abort(400)

    namespace=request.json['namespace']
    services=request.json['services']
    
    pattern = '[a-z0-9]([-a-z0-9]*[a-z0-9])'
    result = re.match(pattern, namespace)

    if not result:
        abort(400)

    # Configs can be set in Configuration class directly or using helper utility
    config.load_kube_config()
    
    # kubernetes api
    v1 = client.CoreV1Api()
    
    # list pods
    namespace_list = v1.list_namespace()

    # create a namespace
    subprocess.call('kubectl create namespace ' + str(namespace), shell=True)

    # open folders
    for folder in services:
        
        # list the yamls
        yamls_list = os.listdir(os.path.join(STATIC_FOLDER, folder))
        yamls_list = [k for k in yamls_list if '.yaml' in k]

        # open each yaml
        for yamls_item in yamls_list:

            # open yaml files
            with open(os.path.join(STATIC_FOLDER, folder, yamls_item)) as file:

                # load yaml
                dep = yaml.safe_load(file)

            if yamls_item == 'nginx-service.yaml':
                dep['spec']['ports'][0]['nodePort'] = dep['spec']['ports'][0]['nodePort'] + (len(namespace_list.items) - 4)

            # edit
            dep['metadata']['name'] = dep['metadata']['name'] + '-' + str(namespace)
            dep['metadata']['namespace'] = str(namespace)

            if yamls_item == 'nginx-service.yaml':
                print(dep)

            # save yaml
            with open(os.path.join(STATIC_FOLDER, 'edited_file.yaml'), 'w') as outfile:
                yaml.dump(dep, outfile, default_flow_style=False)

            # deploy
            subprocess.call('kubectl apply -f ' + STATIC_FOLDER + '/' + 'edited_file.yaml', shell=True)

    # return
    return jsonify({"result":"sucess"})

#+--------------------------------------------------------+
#| delete()                                               |
#+--------------------------------------------------------+
@app.route('/api/v1.0/delete', methods=['PUT'])
def delete_repository():
        
    #  {
    #      "namespace": "gabriel",
    #  }

    if not request.json or not 'namespace' in request.json:
        abort(400)
    
    namespace=request.json['namespace']
            
    pattern = '[a-z0-9]([-a-z0-9]*[a-z0-9])'
    result = re.match(pattern, namespace)

    if not result:
        abort(400)

    # delete namespace
    subprocess.call('kubectl delete namespace ' + str(namespace), shell=True)

    # return
    return jsonify({"result":"sucess"})

if __name__ == '__main__':
    app.run(get_env_variable("HOST_IP"), debug=True, port=8070)
