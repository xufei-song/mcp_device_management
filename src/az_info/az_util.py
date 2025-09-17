import subprocess

def get_az_command():
    """
    Get the correct Azure CLI command path
    """
    common_paths = [
        "az",  # If it's in PATH
        r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",  # Default installation path
        r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"  # Alternative path
    ]
    
    for az_path in common_paths:
        try:
            subprocess.run([az_path, "--version"], capture_output=True, text=True, check=True, timeout=5)
            return az_path
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    return "az"  # Fallback to default

def az_login():
    try:
        az_cmd = get_az_command()
        subprocess.run([az_cmd, "login"], check=True)
        print("Login successful.")
        return True  # Return True on success
    except subprocess.CalledProcessError as e:
        print(f"Login failed: {e}")
        return None


def get_user_info():
    """
    Get current user information including email address
    """
    try:
        az_cmd = get_az_command()
        
        # Get account information
        result = subprocess.run(
            [az_cmd, "account", "show", "--query", "{name:name, user:user, tenantId:tenantId}", "--output", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        
        import json
        user_info = json.loads(result.stdout.strip())
        return user_info
    except subprocess.CalledProcessError as e:
        print(f"Error getting user info: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing user info JSON: {e}")
        return None


def get_user_email():
    """
    Get current user's email address
    """
    user_info = get_user_info()
    if user_info and 'user' in user_info and 'name' in user_info['user']:
        return user_info['user']['name']
    return None


# https://microsoft.visualstudio.com/_apis
def get_azure_token():
    try:
        az_cmd = get_az_command()
        result = subprocess.run(
            [az_cmd, "account", "get-access-token", "--resource=499b84ac-1321-427f-aa17-267ca6975798", "--query", "accessToken", "--output", "tsv"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        return None