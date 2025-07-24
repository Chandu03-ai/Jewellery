param (
    [string]$registryHost,
    [int]$registryPort,
    [bool]$registryAlreadyChecked = $false
)

function Write-Info($msg) {
    Write-Host "`n[INFO] $msg" -ForegroundColor Cyan
}

function Write-ErrorAndExit($msg) {
    Write-Host "`n[ERROR] $msg" -ForegroundColor Red
    exit 1
}

# Prompt for registry info if not provided
if (-not $registryHost) {
    $registryHost = Read-Host "Enter the registry host IP (default: 192.168.0.104)"
    if ([string]::IsNullOrWhiteSpace($registryHost)) {
        $registryHost = "192.168.0.104"
    }
}

if (-not $registryPort) {
    $inputPort = Read-Host "Enter the registry port (default: 5000)"
    if ([string]::IsNullOrWhiteSpace($inputPort)) {
        $registryPort = 5000
    } else {
        $registryPort = [int]$inputPort
    }
}

# Prompt for image name and build context
$imageName = Read-Host "Enter the image name (default: jewellery-inventory-api:latest)"
if ([string]::IsNullOrWhiteSpace($imageName)) {
    $imageName = "jewellery-inventory-api:latest"
}

$buildContextPath = Read-Host "Enter the Docker build context path (default: ../jewelleryApi)"
if ([string]::IsNullOrWhiteSpace($buildContextPath)) {
    $buildContextPath = "../jewelleryApi"
}

# Final image tag with registry
$registryImage = "${registryHost}:${registryPort}/$imageName"

Write-Info "Using registry: ${registryHost}:${registryPort}"
Write-Info "Building image: $registryImage"
Write-Info "Build context path: $buildContextPath"

# Step 1: Check if registry is reachable unless already checked
if (-not $registryAlreadyChecked) {
    Write-Info "Checking if Docker registry is reachable at http://${registryHost}:${registryPort}..."
    try {
        $response = Invoke-WebRequest -Uri "http://${registryHost}:${registryPort}/v2/_catalog" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Info "Docker registry is reachable."
        } else {
            Write-ErrorAndExit "Registry responded with unexpected status code: $($response.StatusCode)"
        }
    } catch {
        Write-ErrorAndExit "Failed to reach Docker registry at ${registryHost}:${registryPort}"
    }
} else {
    Write-Info "Skipping registry reachability check (already verified earlier)."
}

# Step 2: Build image directly with full registry tag
Write-Info "Building Docker image..."
docker build -t $registryImage $buildContextPath
if ($LASTEXITCODE -ne 0) {
    Write-ErrorAndExit "Docker build failed."
}

# Step 3: Push to registry
Write-Info "Pushing image to ${registryImage}..."
docker push $registryImage
if ($LASTEXITCODE -ne 0) {
    Write-ErrorAndExit "Push failed."
}

# Final output
Write-Info "API image build & push successful!"
Write-Host "Pull it using:" -ForegroundColor Green
Write-Host "docker pull $registryImage" -ForegroundColor Yellow
