#!/bin/bash

script_dir="$(dirname "$0")"

"$script_dir"/venv/bin/python "$script_dir"/get_gpu_types.py
