#!/bin/bash
script_dir="$(dirname "$0")"

echo "Setting up virtual environment..."
if [ ! -d "$script_dir/venv" ]
then
    python -m venv "$script_dir/venv"
fi
echo "Activating virtual environment..."
# shellcheck disable=SC1090
source "$script_dir/venv/bin/activate"
echo "Installing requirements..."
pip install -r "$script_dir/requirements.txt"

echo "Setup complete"

exit 0