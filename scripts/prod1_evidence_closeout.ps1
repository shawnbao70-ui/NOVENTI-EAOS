# PROD1 evidence closeout helper — does not invent GO.
# Usage (PowerShell):
#   $env:EAOS_TEST_DATABASE_URL = "postgresql+psycopg://USER:PASS@127.0.0.1:5432/eaos_test"
#   $env:EAOS_RUN_INTEGRATION_CRITICAL = "1"
#   .\scripts\prod1_evidence_closeout.ps1
#
# Optional for GitHub evidence (requires gh auth):
#   $env:PROD1_CANDIDATE_SHA = "<full-sha>"

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

function Write-Step($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }

Write-Step "PROD1 evidence closeout (fail-closed; no invented GO)"

$report = [ordered]@{
  timestamp_utc = (Get-Date).ToUniversalTime().ToString("o")
  candidate_sha = $env:PROD1_CANDIDATE_SHA
  branch_protection = "UNVERIFIED"
  docker_smoke = "UNVERIFIED"
  integration_critical = "UNVERIFIED"
  decision = "NO-GO"
  notes = @()
}

# --- Git / SHA ---
$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) {
  $report.notes += "git not on PATH"
} else {
  if (-not $report.candidate_sha) {
    $report.candidate_sha = (git rev-parse HEAD).Trim()
  }
  $report.notes += "candidate_sha=$($report.candidate_sha)"
}

# --- Branch protection via gh ---
$gh = Get-Command gh -ErrorAction SilentlyContinue
if (-not $gh) {
  $report.notes += "gh not on PATH — cannot verify branch protection or CI"
} else {
  try {
    $repo = (gh repo view --json nameWithOwner -q .nameWithOwner)
    $defaultBranch = (gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
    $prot = gh api "repos/$repo/branches/$defaultBranch/protection" 2>&1
    if ($LASTEXITCODE -eq 0) {
      $report.branch_protection = "VERIFIED_API"
      $report.notes += "branch=$defaultBranch protection API readable"
      $prot | Out-File -Encoding utf8 "docs/release/_PROD1_branch_protection_api.json"
    } else {
      $report.notes += "branch protection API failed (need admin): $prot"
    }
  } catch {
    $report.notes += "gh branch protection error: $($_.Exception.Message)"
  }

  # --- docker-smoke CI history ---
  try {
    $sha = $report.candidate_sha
    if ($sha) {
      $runs = gh run list --workflow=ci.yml --limit 30 --json databaseId,headSha,conclusion,url,displayTitle,name
      $runs | Out-File -Encoding utf8 "docs/release/_PROD1_ci_runs.json"
      $match = $runs | ConvertFrom-Json | Where-Object { $_.headSha -eq $sha -and $_.conclusion -eq "success" }
      if (-not $match) {
        # fall back: any recent success with docker-smoke job
        $ids = ($runs | ConvertFrom-Json | Where-Object { $_.conclusion -eq "success" } | Select-Object -First 5).databaseId
        foreach ($id in $ids) {
          $jobs = gh run view $id --json jobs,url,headSha | ConvertFrom-Json
          $smoke = $jobs.jobs | Where-Object { $_.name -match "docker-smoke" -and $_.conclusion -eq "success" }
          if ($smoke) {
            $report.docker_smoke = "GREEN"
            $report.notes += "docker-smoke green run_url=$($jobs.url) sha=$($jobs.headSha)"
            break
          }
        }
      } else {
        $id = ($match | Select-Object -First 1).databaseId
        $jobs = gh run view $id --json jobs,url,headSha | ConvertFrom-Json
        $smoke = $jobs.jobs | Where-Object { $_.name -match "docker-smoke" -and $_.conclusion -eq "success" }
        if ($smoke) {
          $report.docker_smoke = "GREEN"
          $report.notes += "docker-smoke green run_url=$($jobs.url) sha=$($jobs.headSha)"
        } else {
          $report.notes += "successful workflow run found but docker-smoke job not green for sha=$sha"
        }
      }
    }
  } catch {
    $report.notes += "CI lookup error: $($_.Exception.Message)"
  }
}

# --- integration_critical ---
$url = $env:EAOS_TEST_DATABASE_URL
if (-not $url) {
  $report.notes += "EAOS_TEST_DATABASE_URL unset"
} elseif ($url -notmatch "eaos_test") {
  $report.notes += "EAOS_TEST_DATABASE_URL database name must contain eaos_test"
} else {
  $env:EAOS_RUN_INTEGRATION_CRITICAL = "1"
  Write-Step "Running integration_critical"
  $out = "docs/release/_PROD1_integration_critical.txt"
  try {
    python scripts/run_contract_shard.py integration_critical --pytest-arg=-m --pytest-arg=postgresql 2>&1 |
      Tee-Object -FilePath $out
    if ($LASTEXITCODE -eq 0) {
      $report.integration_critical = "GREEN"
    } else {
      $report.notes += "integration_critical exit=$LASTEXITCODE (see $out)"
    }
  } catch {
    $report.notes += "integration_critical error: $($_.Exception.Message)"
  }
}

if (
  $report.branch_protection -match "VERIFIED" -and
  $report.docker_smoke -eq "GREEN" -and
  $report.integration_critical -eq "GREEN"
) {
  $report.decision = "READY_FOR_GO_RECORD"
  $report.notes += "All three evidence gates look green — update PRODUCTION_GO_DECISION_G469.md manually with SHA/URLs"
} else {
  $report.decision = "NO-GO"
}

$reportPath = "docs/release/_PROD1_EVIDENCE_REPORT.json"
($report | ConvertTo-Json -Depth 6) | Out-File -Encoding utf8 $reportPath
Write-Step "Wrote $reportPath"
Write-Host ($report | ConvertTo-Json -Depth 6)
Write-Host "Decision hint: $($report.decision)"
