import os
import subprocess

def initialize_git_repository(repo_name, directory=".", user_name=None, user_email=None, branch_name="master"):
    # Set the repository path
    repo_path = os.path.join(directory, repo_name)
    # Create the directory for the repository
    os.makedirs(repo_path, exist_ok=True)
    
    # Initialize the git repository
    subprocess.run(["git", "init", "-b", branch_name], cwd=repo_path, check=True)
    
    # Set user.name and user.email if provided
    if user_name:
        subprocess.run(["git", "config", "user.name", user_name], cwd=repo_path, check=True)
    if user_email:
        subprocess.run(["git", "config", "user.email", user_email], cwd=repo_path, check=True)
    
    # Additional Git settings
    subprocess.run(["git", "config", "core.autocrlf", "input"], cwd=repo_path, check=True)  # Handle line endings
    subprocess.run(["git", "config", "init.defaultBranch", branch_name], cwd=repo_path, check=True)  # Default branch
    subprocess.run(["git", "config", "pull.rebase", "false"], cwd=repo_path, check=True)  # Pull strategy
    
    # Add all files in the directory to the repository and codespace workspace
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.relpath(os.path.join(root, file), start=directory)
            subprocess.run(["git", "add", file_path], cwd=repo_path, check=True)
    
    # Commit the added files to the repository
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True)
    
    # Push the changes to the branch 'kdawg'
    subprocess.run(["git", "branch", "-M", "kdawg"], cwd=repo_path, check=True)
    subprocess.run(["git", "remote", "add", "origin", f"codespace_workspace/{repo_name}.git"], cwd=repo_path, check=True)
    subprocess.run(["git", "push", "-u", "origin", "kdawg"], cwd=repo_path, check=True)
    # Create the directory for the repository
    os.makedirs(repo_path, exist_ok=True)
    
    # Initialize the git repository
    subprocess.run(["git", "init", "-b", branch_name], cwd=repo_path, check=True)
    
    # Set user.name and user.email if provided
    if user_name:
        subprocess.run(["git", "config", "user.name", user_name], cwd=repo_path, check=True)
    if user_email:
        subprocess.run(["git", "config", "user.email", user_email], cwd=repo_path, check=True)
    
    # Additional Git settings
    subprocess.run(["git", "config", "core.autocrlf", "input"], cwd=repo_path, check=True)  # Handle line endings
    subprocess.run(["git", "config", "init.defaultBranch", branch_name], cwd=repo_path, check=True)  # Default branch
    subprocess.run(["git", "config", "pull.rebase", "false"], cwd=repo_path, check=True)  # Pull strategy
    
    print(f"Initialized empty Git repository in {repo_path} with branch '{branch_name}'")
    if user_name and user_email:
        print(f"Configured user.name as '{user_name}' and user.email as '{user_email}'")

# Example usage
directory = "/data/data/com.termux/files/home/prog/"
initialize_git_repository(
    "my_new_repository", 
    directory, 
    user_name="kkor", 
    user_email="nilrok.nivek@gmail.com", 
    branch_name="kdawg"
)

