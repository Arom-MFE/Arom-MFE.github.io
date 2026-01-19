# Personal Website

This repository contains my personal website with live PCR (Put-Call Ratio) analysis.

## Automatic Updates

The PCR analysis data is automatically updated every 6 hours via GitHub Actions:
- **Schedule:** Every 6 hours (00:00, 06:00, 12:00, 18:00 UTC)
- **Workflow:** `.github/workflows/generate-snapshot.yml`
- **Script:** `generate_snapshot.py`

The workflow generates fresh snapshot files:
- `latest_table.json` - All analysis tables and data
- `latest_plot_pcr.png` - PCR by expiry plot
- `latest_plot_impulse.png` - Hedging impulse timeline
- `latest_plot_eventscore.png` - Event score timeline

## Manual Trigger

You can manually trigger an update:
1. Go to **Actions** tab in GitHub
2. Click **"Generate PCR Snapshot"**
3. Click **"Run workflow"**

## Files Structure

All files are in the root directory (flat structure) for GitHub Pages compatibility.
