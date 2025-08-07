param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$vmName,

    [Parameter(Mandatory=$true, Position=1)]
    [string]$isoPath,

    [Parameter(Mandatory=$true, Position=2)]
    [string]$vmPath
)

# 指定されたパス配下にVMごとのルートフォルダパスを構成
$vmRootPath = Join-Path -Path $vmPath -ChildPath $vmName
# Hyper-Vの標準レイアウトに従い、VHDXのパスを構成
$vhdPath = Join-Path -Path $vmRootPath -ChildPath "Virtual Hard Disks\$($vmName).vhdx"

$memory = 32GB
$vhdSize = 500GB
$cpuCount = 8

# VM 作成
# VMごとにファイルを格納する専用フォルダを作成し、-Path に指定します。
New-VM -Name $vmName `
    -MemoryStartupBytes $memory `
    -Generation 2 `
    -NewVHDPath $vhdPath `
    -NewVHDSizeBytes $vhdSize `
    -Path $vmRootPath

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
