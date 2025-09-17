#!/usr/bin/env python3
"""
Azure DevOps Deliverable Recording Script

This script demonstrates how to use azure CLI utilities to get access tokens
and interact with Azure DevOps services.
"""

import sys
import subprocess
from az_util import az_login, get_azure_token, get_user_info, get_user_email
from deliverable_handler import AzureDevOpsClient


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


def main():
    """
    Main function to demonstrate Azure token retrieval
    """
    print("=" * 50)
    print("Azure DevOps Token Retrieval Demo")
    print("=" * 50)
    
    # Step 0: Check if Azure CLI is available
    print("\n[INFO] Checking Azure CLI availability...")
    az_path = check_azure_cli()
    if not az_path:
        print("[ERROR] Azure CLI not found!")
        print("Please install Azure CLI first:")
        print("- Download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows")
        print("- Or install via winget: winget install -e --id Microsoft.AzureCLI")
        print("- Then restart your terminal/PowerShell session")
        return 1
    
    print("[SUCCESS] Azure CLI found!")
    
    # Step 1: Attempt to login (this may prompt for interactive login)
    print("\n[INFO] Attempting Azure CLI login...")
    login_result = az_login()
    
    if login_result is None:
        print("[ERROR] Login failed. Please ensure Azure CLI is installed and configured.")
        return 1
    
    # Step 1.5: Get user information
    print("\n[INFO] Retrieving user information...")
    user_info = get_user_info()
    user_email = get_user_email()
    
    if user_info:
        print("\n[SUCCESS] User information retrieved!")
        print("-" * 50)
        print("User Name:", user_info.get('name', 'N/A'))
        print("User Email:", user_email or 'N/A')
        print("Tenant ID:", user_info.get('tenantId', 'N/A'))
        if 'user' in user_info:
            print("User Type:", user_info['user'].get('type', 'N/A'))
        print("-" * 50)
    else:
        print("[WARNING] Could not retrieve user information, but login was successful.")
    
    # Step 2: Get the access token
    print("\n[INFO] Retrieving Azure access token...")
    token = get_azure_token()
    
    if token:
        print("\n[SUCCESS] Access token retrieved successfully!")
        print("-" * 50)
        print("Token preview (first 20 characters):", token[:20] + "...")
        print("Token length:", len(token))
        print("-" * 50)
        
        # For debugging purposes, you can uncomment the line below to see the full token
        # WARNING: Never log full tokens in production!
        # print("Full token:", token)
        
        # Step 3: Query deliverable information
        print("\n[INFO] Querying deliverable information...")
        try:
            # Create Azure DevOps client
            devops_client = AzureDevOpsClient(
                personal_access_token=token
            )
            
            # Query specific deliverable
            deliverable_id = 59278704
            print(f"[INFO] Querying deliverable ID: {deliverable_id}")
            
            deliverable_info = devops_client.get_deliverable_info(deliverable_id)
            
            if deliverable_info:
                print("\n[SUCCESS] Deliverable information retrieved!")
                devops_client.print_deliverable_info(deliverable_info)
                
                # Step 4: Add comment to deliverable
                print("\n[INFO] Adding test comment to deliverable...")
                comment_success = devops_client.update_deliverable_with_comment(
                    deliverable_id, 
                    "this is test"
                )
                
                if not comment_success:
                    print("[WARNING] Failed to add comment, but deliverable query was successful")
                
            else:
                print(f"[ERROR] Could not retrieve deliverable {deliverable_id}")
                print("Possible reasons:")
                print("1. Deliverable ID does not exist")
                print("2. No permission to access this deliverable")
                print("3. Deliverable is in a different project")
                return 1
            
        except Exception as e:
            print(f"[ERROR] Exception while querying deliverable: {e}")
            print("This might be due to:")
            print("1. Invalid token or expired session")
            print("2. Network connectivity issues")
            print("3. Azure DevOps service unavailable")
            return 1
        
        return 0
    else:
        print("\n[ERROR] Failed to retrieve access token.")
        print("Please check:")
        print("1. Azure CLI is installed and logged in")
        print("2. You have proper permissions")
        print("3. The resource ID is correct")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
