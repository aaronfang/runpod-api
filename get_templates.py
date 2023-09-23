import requests
from collections import defaultdict

def get_docker_image_tags(repo):
    r = requests.get(f'https://registry.hub.docker.com/v2/repositories/{repo}/tags')
    return r.json()['results']

def get_latest_tags(repo):
    tags = get_docker_image_tags(repo)
    prefix_dict = defaultdict(list)

    # 将标签按前缀分类
    for tag in tags:
        prefix = tag["name"].rsplit("-", 1)[0]
        try:
            version = tuple(map(int, tag["name"].rsplit("-", 1)[-1].split(".")))
            prefix_dict[prefix].append((version, tag))
        except ValueError:
            # 忽略不能转换为整数的版本号
            pass

    # 对每个前缀，找出最新的标签
    latest_tags = []
    for prefix, version_tag_pairs in prefix_dict.items():
        latest_version, latest_tag = max(version_tag_pairs)
        latest_tags.append(f'{repo}:{latest_tag["name"]}')

    return latest_tags

# repo = 'runpod/stable-diffusion'
# latest_tags = get_latest_tags(repo)
# for tag in latest_tags:
#     print(tag)