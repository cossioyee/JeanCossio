param(
    [string]$vmname
)
$VMPath = "E:\$vmname"
$VHDPath = "$VMPath\$vmname.vhdx"
$VHDSize = 60GB
$MemoryStartupBytes = 8GB
$SwitchName = "Kubs External Switch"
$CPUCount = 4
$ISOPath = "C:\Users\Admin\Downloads\CentOS-Stream-9-latest-x86_64-dvd1.iso"

# Crear carpeta para la VM
New-Item -ItemType Directory -Path $VMPath -Force

# Crear disco duro virtual
New-VHD -Path $VHDPath -SizeBytes $VHDSize -Dynamic

# Crear la VM
New-VM `
  -Name $vmname `
  -MemoryStartupBytes $MemoryStartupBytes `
  -Generation 2 `
  -VHDPath $VHDPath `
  -Path $VMPath `
  -SwitchName $SwitchName

# Configurar procesadores
Set-VMProcessor -vmname $vmname -Count $CPUCount

# Conectar la ISO para instalación
Add-VMDvdDrive -vmname $vmname -Path $ISOPath

# Establecer orden de arranque: DVD primero
Set-VMFirmware -vmname $vmname -FirstBootDevice (Get-VMFirmware -vmname $vmname).BootOrder | Where-Object Device -like "*CD*"

# (Opcional) Configurar red fija o NAT, si aplica
Add-VMNetworkAdapter -vmname $vmname -SwitchName "vSwitchNAT"

# # Iniciar la VM
# Start-VM -Name $vmname
