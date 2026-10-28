param(
  [Parameter(Mandatory = $true)][string]$Pptx,
  [Parameter(Mandatory = $true)][string]$Pdf,
  [string]$PngDir = ""
)

$ErrorActionPreference = "Stop"
$ppt = New-Object -ComObject PowerPoint.Application
try {
  $pres = $ppt.Presentations.Open($Pptx, $true, $false, $false)
  try {
    $pres.SaveAs($Pdf, 32)
    Write-Output ("pdf: " + $Pdf)
    if ($PngDir -ne "") {
      if (-not (Test-Path -LiteralPath $PngDir)) { New-Item -ItemType Directory -Path $PngDir | Out-Null }
      $n = $pres.Slides.Count
      for ($i = 1; $i -le $n; $i++) {
        $file = Join-Path $PngDir ("slide-{0:d2}.png" -f $i)
        $pres.Slides.Item($i).Export($file, "PNG", 1600, 900)
      }
      Write-Output ("png count: " + $n)
    }
  } finally {
    $pres.Close()
  }
} finally {
  $ppt.Quit()
}
