# Green-AI Code Scanner GitHub Action

Scan your code for energy inefficiency and sustainability debt natively in your CI/CD pipeline using the Green-AI GitHub Action.

## Inputs

| Input | Description | Required | Default |
| --- | --- | --- | --- |
| `target` | Path(s) to scan. Space-separated. | No | `.` |
| `output` | Path to output file. | No | |
| `format` | Output format (`csv`, `json`, `html`, `pdf`). | No | |
| `config` | Path to `.green-ai.yaml` config file. | No | |
| `fail-on` | Fail the action if violations of this severity or higher are found (`critical`, `high`, `medium`, `low`). | No | |
| `git-url` | Git repository URL to scan. | No | |
| `branch` | Specific branch to checkout (for git-url). | No | |

## Outputs

This action does not currently define specific outputs in `action.yml`, but you can use the `output` file configured via the inputs in subsequent steps (e.g., uploading the report as an artifact).

## Example Workflow Usage

```yaml
name: Green-AI Scan

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Run Green-AI Scanner
        uses: green-ai/green-ai-action@main
        with:
          target: './src'
          fail-on: 'high'
          format: 'html'
          output: 'green-ai-report.html'

      - name: Upload Report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: green-ai-report
          path: green-ai-report.html
```
