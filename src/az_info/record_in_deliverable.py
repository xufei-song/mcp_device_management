#!/usr/bin/env python3
"""
Azure DevOps Deliverable Recording Script

This script demonstrates how to use azure CLI utilities to get access tokens
and interact with Azure DevOps services.
"""

import sys
import subprocess
from pathlib import Path

# 确保可以导入同目录下的模块
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from az_util import az_login, get_azure_token, get_user_info, get_user_email
from deliverable_handler import AzureDevOpsClient


def az_logout():
    """
    执行Azure CLI登出
    """
    try:
        from az_util import get_az_command
        az_cmd = get_az_command()
        result = subprocess.run([az_cmd, "logout"], capture_output=True, text=True, check=True)
        print("[INFO] Azure logout successful")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[WARNING] Azure logout failed: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Exception during logout: {e}")
        return False


def check_azure_cli():
    """
    Check if Azure CLI is available
    """
    try:
        # Try common Azure CLI installation paths
        common_paths = [
            "az",  # If it's in PATH
            r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",  # Default installation path
            r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"  # Alternative path
        ]
        
        for az_path in common_paths:
            try:
                result = subprocess.run([az_path, "--version"], capture_output=True, text=True, check=True, timeout=10)
                print(f"[SUCCESS] Found Azure CLI at: {az_path}")
                return az_path
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                continue
        
        return None
    except Exception as e:
        print(f"[ERROR] Exception while checking Azure CLI: {e}")
        return None


def record_in_deliverable(comment_text):
    """
    在deliverable中记录comment
    
    Args:
        comment_text (str): 要添加到deliverable discussion中的评论内容
    
    Returns:
        tuple: 成功返回(True, user_email)，失败返回(False, None)
    """
    azure_devops_client = None
    login_successful = False
    user_email = None
    
    try:
        print("[INFO] Initializing Azure connection...")
        
        # Step 1: Check Azure CLI
        az_path = check_azure_cli()
        if not az_path:
            print("[ERROR] Azure CLI not found!")
            return False, None
        
        # Step 2: Login
        login_result = az_login()
        if login_result is None:
            print("[ERROR] Azure login failed!")
            return False, None
        
        login_successful = True  # 标记登录成功
        
        # Step 3: Get user email
        user_email = get_user_email()
        if user_email:
            print(f"[INFO] Current user email: {user_email}")
        else:
            print("[WARNING] Failed to get user email, but continuing...")
        
        # Step 4: Get token
        token = get_azure_token()
        if not token:
            print("[ERROR] Failed to get Azure token!")
            return False, None
        
        # Step 5: Create client
        azure_devops_client = AzureDevOpsClient(personal_access_token=token)
        print("[SUCCESS] Azure connection initialized!")
        
        # 使用固定的deliverable ID
        deliverable_id = 59278704
        
        print(f"[INFO] Recording comment in deliverable {deliverable_id}: {comment_text}")
        
        # 添加comment到deliverable
        success = azure_devops_client.update_deliverable_with_comment(
            deliverable_id, 
            comment_text
        )
        
        if success:
            print(f"[SUCCESS] Comment recorded successfully: {comment_text}")
            return True, user_email
        else:
            print(f"[ERROR] Failed to record comment: {comment_text}")
            return False, None
            
    except Exception as e:
        print(f"[ERROR] Exception while recording comment: {e}")
        return False, None
        
    finally:
        # 清理：如果登录成功，执行登出
        if login_successful:
            print("[INFO] Cleaning up: performing Azure logout...")
            az_logout()


def main():
    """
    Main function for testing - demonstrates the record_in_deliverable interface
    """
    print("=" * 50)
    print("Azure DevOps Deliverable Recording Test")
    print("=" * 50)
    
    # Test the record_in_deliverable interface
    test_comment = "this is test"
    success, user_email = record_in_deliverable(test_comment)
    
    if success:
        print(f"\n[SUCCESS] Test completed successfully!")
        if user_email:
            print(f"[INFO] User email: {user_email}")
        return 0
    else:
        print(f"\n[ERROR] Test failed!")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
