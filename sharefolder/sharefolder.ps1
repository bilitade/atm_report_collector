# Specify the path to the folder you want to share
$folderPath = "D:\ejlogs"
$shareName = "EJLOGS"

# Check if the script is running as an administrator
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Script must be run as administrator. Please run PowerShell as an administrator and try again."
    exit
}

# Check if the share already exists
$existingShare = Get-SmbShare | Where-Object { $_.Name -eq $shareName }

if ($existingShare -ne $null) {
    Write-Host "Share '$shareName' already exists. Exiting."
    exit
}

# Create a new share
try {
    New-SmbShare -Name $shareName -Path $folderPath -FullAccess "Everyone"
    Write-Host "Share '$shareName' created successfully."
}
catch {
    Write-Host "Error creating the share: $_"
    exit
}

# Configure share permissions
try {
    $share = Get-SmbShare $shareName
    $acl = Get-SmbShareAccess $shareName -Name Everyone -ErrorAction SilentlyContinue

    # Grant Everyone read access to the share
    if ($acl -eq $null) {
        Grant-SmbShareAccess -Name $shareName -AccountName Everyone -AccessRight Read -Force
        Write-Host "Read access granted to Everyone on share '$shareName'."
    }
}
catch {
    Write-Host "Error configuring share permissions: $_"
    exit
}

# Set NTFS permissions on the folder
try {
    $acl = Get-Acl $folderPath
    $permission = "Everyone", "Read", "Allow"
    $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule $permission

    # Set the access rule on the folder
    $acl.AddAccessRule($accessRule)
    Set-Acl -Path $folderPath -AclObject $acl

    Write-Host "NTFS permissions set on folder '$folderPath'."
}
catch {
    Write-Host "Error setting NTFS permissions: $_"
    exit
}

Write-Host "Folder '$folderPath' has been shared as '$shareName' with Everyone having Read access."
