$vmName = "win11-vm"
$isoPath = ".\iso\Win11_24H2_Japanese_x64.iso"
$vmPath = ".\vm\$vmName"
$vhdPath = "$vmPath\$vmName.vhdx"
$memory = 32GB
$vhdSize = 500GB
$cpuCount = 8

# VM 作成
New-VM -Name $vmName `
    -MemoryStartupBytes $memory `
    -Generation 2 `
    -NewVHDPath $vhdPath `
    -NewVHDSizeBytes $vhdSize `
    -Path $vmPath

# CPUコア数の設定
Set-VMProcessor -VMName $vmName -Count $cpuCount

# キープロテクターの設定 (TPM有効化の前提条件)
Set-VMKeyProtector -VMName $vmName -NewLocalKeyProtector

# トラステッドプラットフォームモジュール (TPM) の有効化
Enable-VMTPM -VMName $vmName

# ISO接続
Add-VMDvdDrive -VMName $vmName -Path $isoPath

# DVDドライブを最初の起動デバイスに設定
$dvdDrive = Get-VMDvdDrive -VMName $vmName
Set-VMFirmware -VMName $vmName -FirstBootDevice $dvdDrive
