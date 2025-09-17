import argparse
import subprocess
import itertools
import threading
import time
import sys
from az_util import az_login, get_azure_token
from deliverable_handler import AzureDevOpsClient 

def install_package(package_name):
    try:
        subprocess.run(["pip3", "install", package_name], check=True)
        print(f"Package {package_name} installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install package {package_name}: {e}")

def welcome_animation():
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if done:
            break
        sys.stdout.write('\rWelcome to EUX Test Device Management Script ' + c)
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\rWelcome to EUX Test Device Management Script!     \n')

def main():
    
    # global done
    # done = False
    # t = threading.Thread(target=welcome_animation)
    # t.start()
    # time.sleep(3)  # 显示动画3秒钟
    # done = True
    # t.join()

    # 安装 azure-devops 包
    install_package("azure-devops")

    az_login()

    personal_access_token = get_azure_token()
    if personal_access_token:
        print(f"Get Token succeed.")
    else:
        print("Failed to get access token.")

    client = AzureDevOpsClient(personal_access_token)
    client.create_deliverable_with_parent(
        title="New Deliverable",
        description="Description of the deliverable",
        parent_url="https://microsoft.visualstudio.com/OS/_workitems/edit/55296113"
    )


if __name__ == "__main__":
    main()