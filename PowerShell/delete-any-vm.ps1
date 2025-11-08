param(
    [string]$vmname
)
$VMPath = "E:\$vmname"
Stop-VM -Name $vmname -Force
Remove-VM -Name $vmname -Force
Remove-Item -Path $VMPath -Recurse -Force