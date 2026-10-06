# System Log Monitor

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

**System Log Monitor** is a custom integration for Home Assistant that monitors your system logs in real-time, de-duplicates errors and warnings, and turns them into actionable Home Assistant **Repairs** issues.

## Features

* **UI Configurable**: Easily toggle error or warning tracking straight from the Home Assistant UI.
* **Smart De-duplication**: Prevents notification spam by tracking log entry fingerprints.
* **Custom Repairs Actions**: Every issue provides a guided repairs flow with three options:
  1. **Report as GitHub issue**: Directs you with quick links to log text and GitHub.
  2. **I've fixed this**: Dismisses the repair issue until it happens again.
  3. **Ignore this log message**: Adds the message to a persistent ignore list.
* **Ignore List Management**: View and clean up your ignored logs directly via the integration's Options flow.

## Installation via HACS

1. Open **HACS** in your Home Assistant instance.
2. Click on the three dots in the top right corner and select **Custom repositories**.
3. Add your GitHub repository URL (`https://github.com/your-username/system_log_monitor`) and select **Integration** as the category.
4. Click **Download**, then restart Home Assistant.

## Configuration

1. Go to **Settings > Devices & Services > Add Integration**.
2. Search for **System Log Monitor** and follow the configuration steps.