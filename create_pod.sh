#!/bin/bash
script_dir="$(dirname "$0")"

"${script_dir}/venv/bin/python" "${script_dir}/create_pod.py" "$@"
