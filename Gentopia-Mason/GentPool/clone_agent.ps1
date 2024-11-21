# Get the base agent name from the first argument
$base_agent = $args[0]

# Get the clone agent name from the second argument
$clone_agent = $args[1]

# Check if base agent directory exists
if (-Not (Test-Path "./gentpool/pool/$base_agent")) {
    Write-Host "Base agent directory ./gentpool/pool/$base_agent does not exist. Exiting..."
    exit 1
}

# Check if clone agent directory already exists
if (Test-Path "./gentpool/pool/$clone_agent") {
    Write-Host "Clone agent directory ./gentpool/pool/$clone_agent already exists. Exiting..."
    exit 1
}

# Directory paths
$base_dir_path = "./gentpool/pool/$base_agent"
$clone_dir_path = "./gentpool/pool/$clone_agent"

Write-Host "Cloning agent $base_agent to $clone_agent, continue? (y/n)"
$answer = Read-Host

if ($answer -match '^[Yy]') {
    # Copy the entire base agent directory to the clone agent directory
    Copy-Item -Recurse -Path $base_dir_path -Destination $clone_dir_path

    # Register the clone agent in the pool
    Add-Content -Path "./gentpool/pool/__init__.py" -Value "from .$clone_agent import *"

    # Update the agent names in the clone agent directory
    if ($IsMacOS) {
        # Mac OSX
        (Get-Content "$clone_dir_path/__init__.py") -replace $base_agent, $clone_agent | Set-Content "$clone_dir_path/__init__.py"
        (Get-Content "$clone_dir_path/agent.yaml") -replace "name: $base_agent", "name: $clone_agent" | Set-Content "$clone_dir_path/agent.yaml"
    }
    else {
        # Windows, Linux, other
        (Get-Content "$clone_dir_path/__init__.py") -replace $base_agent, $clone_agent | Set-Content "$clone_dir_path/__init__.py"
        (Get-Content "$clone_dir_path/agent.yaml") -replace "name: $base_agent", "name: $clone_agent" | Set-Content "$clone_dir_path/agent.yaml"
    }

    Write-Host "Agent $clone_agent has been cloned from $base_agent."
}
else {
    Write-Host "Exiting..."
    exit 1
}