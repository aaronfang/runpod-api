#!/usr/bin/env python3
import json
import runpod

def get_price(gpu_type_id):
    response = runpod.API().get_gpu_types()
    resp_json = response.json()

    if response.status_code == 200:
        if 'errors' in resp_json:
            print('ERROR:')
            for error in resp_json['errors']:
                print(error['message'])
        else:
            gpu_types = resp_json['data']['gpuTypes']
            for gpu_type in gpu_types:
                if gpu_type['id'] == gpu_type_id:
                    secure_price = gpu_type['securePrice'] if gpu_type['secureCloud'] else None
                    community_price = gpu_type['communityPrice'] if gpu_type['communityCloud'] else None
                    lowest_price = gpu_type['lowestPrice']['minimumBidPrice']
                    return secure_price, community_price, lowest_price

    else:
        print(response.status_code)
        print(json.dumps(resp_json, indent=4, default=str))

    return None, None, None, None