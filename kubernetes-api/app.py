#!flask/bin/python
from flask_httpauth import HTTPBasicAuth
from kubernetes import client, config
from flask import Flask, jsonify
from flask import make_response
from flask_cors import CORS
from flask import request
from flask import url_for
import os 

#env
def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = "Expected environment variable '{}' not set.".format(name)
        raise Exception(message)

#app
app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

#errorhandler
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

#########################################################
# get_pods()                                            #
######################################################### 
@app.route('/api/v1.0/pods', methods=['GET'])
def get_pods():
        
    # Configs can be set in Configuration class directly or using helper utility
    config.load_kube_config()

    v1 = client.CoreV1Api()
    pod_list = v1.list_namespaced_pod("default")
    pod_list_json = []

    for pod in pod_list.items:
        pod_list_json.append({"name": pod.metadata.name,
                              "status": pod.status.phase,
                              "ip": pod.status.pod_ip})
    return jsonify(pod_list_json)

if __name__ == '__main__':
    app.run(get_env_variable("HOST_IP"), debug=True, port=8070)
