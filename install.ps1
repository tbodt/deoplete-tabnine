[Net.ServicePointManager]::SecurityProtocol = "tls12, tls11, tls"

$web = New-Object Net.WebClient
$versionUrl = "https://update.tabnine.com/version"

$version = $web.DownloadString($versionUrl).replace("`n","")

$arch_raw = Get-CimInstance Win32_OperatingSystem | Select-Object 'OSArchitecture' | Format-Table -HideTableHeaders | Out-String

switch ( $arch_raw.Trim().Substring(0,2) ) {
  "64" { $arch = "x86_64" }
  "32" { $arch = "i686" }
}
$triple = ( $arch + "-pc-windows-gnu" )

$path = "$PSScriptRoot\binaries\$version\$triple"

$url = ( "https://update.tabnine.com/$version/$triple/TabNine.exe" )
if (!(Test-Path -Path "$path\TabNine.exe"))  {
  Write-Host "Downloading TabNine executable..."
  New-Item -ItemType directory -Path $path

  Try {
  $web.DownloadFile(
    $url,
    $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath(
      "$path\TabNine.exe"
    )
  )
  Write-Host "Successful!"
  }
  Catch {
    Write-Host $($_.Exception.ToString())
  }
}
