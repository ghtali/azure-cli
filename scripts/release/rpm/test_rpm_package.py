# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import sys
import subprocess

python_version = os.listdir('/usr/lib64/az/lib/')[0]
root_dir = f'/usr/lib64/az/lib/{python_version}/site-packages/azure/cli/command_modules'
mod_list = [mod for mod in sorted(os.listdir(root_dir)) if os.path.isdir(os.path.join(root_dir, mod)) and mod != '__pycache__']

# From Fedora 36, use `/usr/lib64/az/local/lib/` as PYTHONPATH because installation scheme has changed.
# `test_rpm_in_docker.sh` also creates a copy for installed az modules.
# Ref https://docs.fedoraproject.org/en-US/fedora/latest/release-notes/developers/Development_Python/
if os.path.exists('/usr/lib64/az/local/'):
    pytest_base_cmd = f'PYTHONPATH=/usr/lib64/az/local/lib/{python_version}/site-packages python3 -m pytest -x -v --boxed -p no:warnings --log-level=WARN'
else:
    pytest_base_cmd = f'PYTHONPATH=/usr/lib64/az/lib/{python_version}/site-packages python3 -m pytest -x -v --boxed -p no:warnings --log-level=WARN'
pytest_parallel_cmd = '{} -n auto'.format(pytest_base_cmd)
serial_test_modules = ['botservice', 'network', 'cloud', 'appservice']

for mod_name in mod_list:
    cmd = '{} --junit-xml /azure_cli_test_result/{}.xml --pyargs azure.cli.command_modules.{}'.format(
        pytest_base_cmd if mod_name in serial_test_modules else pytest_parallel_cmd, mod_name, mod_name)
    print('Running:', cmd, flush=True)
    exit_code = subprocess.call(cmd, shell=True)
    if exit_code == 5:
        print('No tests found for {}'.format(mod_name))
    elif exit_code != 0:
        sys.exit(exit_code)

exit_code = subprocess.call(['{} --junit-xml /azure_cli_test_result/azure-cli-core.xml --pyargs azure.cli.core'.format(pytest_parallel_cmd)], shell=True)
sys.exit(exit_code)
