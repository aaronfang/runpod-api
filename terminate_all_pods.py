#!/usr/bin/env python3
import runpod
import json

def terminate_pod(pod_id):
    response = runpod.API().terminate_pod(pod_id)
    resp_json = response.json()

    if response.status_code == 200:
        if 'errors' in resp_json:
            print('ERROR:')
            for error in resp_json['errors']:
                print(error['message'])
        else:
            print(f'Pod {pod_id} has been terminated')

if __name__ == '__main__':
    response = runpod.API().get_pods()
    resp_json = response.json()

    if response.status_code == 200:
        if 'errors' in resp_json:
            print('ERROR:')
            for error in resp_json['errors']:
                print(error['message'])
        elif 'data' in resp_json and 'myself' in resp_json['data'] and resp_json['data']['myself'] is not None:
            pod_ids = [pod['id'] for pod in resp_json['data']['myself']['pods']]
            for pod_id in pod_ids:
                terminate_pod(pod_id)
        else:
            print('ERROR: Unable to get a list of pods')
            print(json.dumps(resp_json, indent=4, default=str))
    else:
        print(response.status_code)
        print(json.dumps(resp_json, indent=4, default=str))
