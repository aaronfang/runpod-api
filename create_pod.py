#!/usr/bin/env python3
import runpod
import json
import argparse
from get_price import get_price
import time
import datetime

gpu_type_map = {
    '3090': 'NVIDIA GeForce RTX 3090',
    '3090ti': 'NVIDIA GeForce RTX 3090 Ti',
    '4090': 'NVIDIA GeForce RTX 4090',
    'a5000': 'NVIDIA RTX A5000'
}

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--name', default='waterbears')
parser.add_argument('-i','--image_name', default='runpod/stable-diffusion:web-ui-10.2.1')
parser.add_argument('-g','--gpu_type_id', default='3090')
parser.add_argument('-ct','--cloud_type',default='ALL')
parser.add_argument('-s','--spot', action='store_true', default=False)
parser.add_argument('-od','--os_disk_size_gb', type=int, default=20)
parser.add_argument('-pd','--persistent_disk_size_gb', type=int, default=50)
parser.add_argument('-bp','--bid_price', type=float, default=0.19)
parser.add_argument('-cc','--country_code',default='SK,SE,BE,BG,CA,CZ,FR,NL')
parser.add_argument('-md','--min_download', type=int, default=600)
parser.add_argument('-p','--ports', default='8888/http,7860/http,7861/http,6006/http,4444/http,22/tcp')
parser.add_argument('-e','--user_envs', nargs='*', default=["RUNPOD_STOP_AUTO=1"])

args = parser.parse_args()

current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
args.name = f'{args.name}-{current_time}'

# Replace the short GPU type id with the full name
args.gpu_type_id = gpu_type_map.get(args.gpu_type_id.lower(), args.gpu_type_id)

# Get the minimum bid price for the GPU type
secure_price, community_price, lowest_price = get_price(args.gpu_type_id)

if args.spot:
    if lowest_price is not None:
        args.bid_price = lowest_price
    else:
        print("No suitable server pod found for spot instance.")
        exit()
else:
    if args.cloud_type == 'ALL':
        if secure_price is not None and community_price is not None:
            args.cloud_type = 'SECURE' if secure_price < community_price else 'COMMUNITY'
            args.bid_price = secure_price if secure_price < community_price else community_price
        elif secure_price is not None:
            args.cloud_type = 'SECURE'
            args.bid_price = secure_price
        elif community_price is not None:
            args.cloud_type = 'COMMUNITY'
            args.bid_price = community_price
        else:
            print("No suitable server pod found.")
            exit()
    else:
        if args.cloud_type == 'SECURE':
            if secure_price is not None:
                args.bid_price = secure_price
            else:
                print("No suitable server pod found for SECURE cloud type.")
                exit()
        else:  # args.cloud_type == 'COMMUNITY'
            if community_price is not None:
                args.bid_price = community_price
            else:
                print("No suitable server pod found for COMMUNITY cloud type.")
                exit()

# Convert the user envs to a dict
USER_ENVS = dict(item.split('=') for item in args.user_envs)
envs_str = ',\n'.join([f'{{key: "{k}", value: "{v}"}}' for k, v in USER_ENVS.items()])

def create_spot_pod():
    pod_config = f"""
        countryCode: "",
        minDownload: {args.min_download},
        bidPerGpu: {args.bid_price},
        gpuCount: 1,
        volumeInGb: {args.persistent_disk_size_gb},
        containerDiskInGb: {args.os_disk_size_gb},
        gpuTypeId: "{args.gpu_type_id}",
        cloudType: {args.cloud_type},
        supportPublicIp: true,
        name: "{args.name}",
        dockerArgs: "",
        ports: "{args.ports}",
        volumeMountPath: "/workspace",
        imageName: "{args.image_name}",
        startJupyter: true,
        startSsh: true,
        env: [
            {envs_str}
        ]
    """
    response = runpod.API().create_spot_pod(pod_config)
    resp_json = response.json()
    
    if response.status_code == 200:
        if 'errors' in resp_json:
            print('ERROR:')
            for error in resp_json['errors']:
                print(error['message'])
        else:
            print(json.dumps(resp_json, indent=4, default=str))
    else:
        print(response.status_code)
        print(json.dumps(resp_json, indent=4, default=str))

    # print current price
    secure_price, community_price, lowest_price = get_price(args.gpu_type_id)
    print(f"Current price: {lowest_price}")

    # print(f"spot={args.spot}, cloud_type={args.cloud_type}")
    # print(pod_config)

def create_on_demand_pod():
    pod_config = f"""
        countryCode: "{args.country_code}",
        minDownload: {args.min_download},
        gpuCount: 1,
        volumeInGb: {args.persistent_disk_size_gb},
        containerDiskInGb: {args.os_disk_size_gb},
        gpuTypeId: "{args.gpu_type_id}",
        cloudType: {args.cloud_type},
        supportPublicIp: true,
        name: "{args.name}",
        dockerArgs: "",
        ports: "{args.ports}",
        volumeMountPath: "/workspace",
        imageName: "{args.image_name}",
        startJupyter: true,
        startSsh: true,
        env: [
            {envs_str}
        ]
    """
    response = runpod.API().create_on_demand_pod(pod_config)
    resp_json = response.json()

    if response.status_code == 200:
        if 'errors' in resp_json:

            for error in resp_json['errors']:
                if error['message'] == 'There are no longer any instances available with the requested specifications. Please refresh and try again.':
                    print('No resources currently available. Please try again later.')
                elif error['message'] == 'There are no longer any instances available with enough disk space.':
                    print(error)
                    print('No instances with enough disk space available. Please try again later.')
                else:
                    print('ERROR: ' + error['message'])
        else:
            print(json.dumps(resp_json, indent=4, default=str))
            exit()
    
    # print current price
    secure_price, community_price, lowest_price = get_price(args.gpu_type_id)
    if args.cloud_type == 'SECURE':
        print(f"Current price: {secure_price}")
    else:
        print(f"Current price: {community_price}")

    # print(f"spot={args.spot}, cloud_type={args.cloud_type}")
    # print(pod_config)

if __name__ == '__main__':
    if args.spot:
        create_spot_pod()
    else:
        create_on_demand_pod()

    