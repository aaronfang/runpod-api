# A collection of Python scripts for calling the RunPod GraphQL API

## Getting started

### Clone the repo, create venv and install dependencies

```bash
git clone https://github.com/aaronfang/runpod-api
cd runpod-api
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

### Configure your RunPod API

Add RUNPOD_API_KEY to your environment variables

```bash
export RUNPOD_API_KEY=your-api-key
```

### Useage:

- `create_pod.py`  Create a new pod (on demand / spot)
```bash
python create_pod.py -s -g "NVIDIA RTX A5000" 
```
Possible arguments:

 Argument | Type | Description |
 --- | --- | --- |
 **--spot** | Boolean | Start a spot pod. On demand if without this argument. |
 **--name** | String | Pod name |
 **--image_name** | String | Docker Image name |
 **--gpu_type_id** | String | GPU type ID. Use get_gpu_types.py to get available GPU types |
 **--cloud_type** | String | 'ALL' or 'SECURE' or 'COMMUNITY' |
 **--os_disk_size_gb** | Integer | OS disk size in GB |
 **--persistent_disk_size_gb** | Integer | Persistent disk size in GB |
 **--bid_price** | Float | Spot bid price. Required if spot pod |
 **--country_code** | String | 'SK,SE,BE,BG,CA,CZ,FR,NL' # Country code |
 **--min_download** | Integer | Minimum download speed in MB/s |
 **--ports** | String | Port mapping. Example: "8888/http,22/tcp" |
 **--user_envs** | String | User environment variables. Example: "ENV1=VALUE1,ENV2=VALUE2" |

- `get_pods.py`  Get all pods

- `get_gpu_types.py`  Get available GPU types

- `start_on_demand_pod.py`  Start an on demand pod

- `start_spot_pod.py`  Start a spot pod

- `stop_pod.py --pod_id "your_pod_id"`  Stop a pod

- `terminate_pod.py --pod_id "your_pod_id"` - Terminate a pod

- `terminate_all_pods.py` - Terminate all pods

- `runpod_tab.py` - GUI interface for managing pods

```bash
python runpod_tab.py
```