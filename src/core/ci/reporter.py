from typing import Dict, Any, Optional


class CIReporter:
    def generate_report(self, scan_results: Dict[str, Any], diff_changes: Optional[Dict[str, set]] = None) -> str:
        """
        Generate a Markdown report from scan results.
        If diff_changes is provided, only include issues on changed lines.
        """
        issues = scan_results.get('issues', [])

        # Filter issues if diff provided
        if diff_changes is not None:
            filtered_issues = []
            for issue in issues:
                file_path = issue.get('file')
                line = issue.get('line', 0)

                if not file_path:
                    continue

                matched_file = None
                # Try exact match first
                if file_path in diff_changes:
                    matched_file = file_path
                else:
                    # Try fuzzy match (endswith) to handle absolute vs relative paths
                    for diff_file in diff_changes:
                        # Normalize separators if needed, but assuming / for now
                        if file_path.endswith(diff_file):
                            matched_file = diff_file
                            break
                        # Also check if diff_file ends with file_path (unlikely but possible if cwd varies)

                if matched_file:
                    changed_lines = diff_changes[matched_file]
                    if line in changed_lines:
                        filtered_issues.append(issue)

            issues = filtered_issues

        if not issues:
            return "### 🌿 Green AI Scan: No Violations Found\nGreat job! Your code is efficient and green."

        # Build Report
        title_suffix = " in changed files" if diff_changes is not None else ""
        report = [
            "### 🌿 Green AI Scan Results",
            f"**Found {len(issues)} violations{title_suffix}.**",
            "",
            "| Severity | File | Line | Issue | Remediation |",
            "| :--- | :--- | :--- | :--- | :--- |"
        ]

        # Sort by severity
        severity_order = {
            'critical': 0,
            'major': 1,
            'high': 1,
            'medium': 2,
            'minor': 3,
            'low': 3,
            'info': 4
        }

        sorted_issues = sorted(
            issues,
            key=lambda x: severity_order.get(x.get('severity', 'low').lower(), 99)
        )

        for issue in sorted_issues:
            sev = issue.get('severity', 'low').upper()

            icon = "🔵"
            if sev in ['CRITICAL', 'HIGH', 'MAJOR']:
                icon = "🔴"
            elif sev == 'MEDIUM':
                icon = "🟡"

            file = issue.get('file', 'N/A')
            # If path is absolute, try to make it relative for display
            if '/' in file:
                file = file.split('/')[-1]  # Show just filename to save space in table

            line = issue.get('line', '0')
            msg = issue.get('message', 'N/A')
            rem = issue.get('remediation', 'N/A')

            # Escape pipes in message/remediation
            msg = msg.replace('|', '\\|').replace('\n', ' ')
            rem = rem.replace('|', '\\|').replace('\n', ' ')

            report.append(f"| {icon} {sev} | `{file}` | {line} | {msg} | {rem} |")

        report.append("")

        # Add summary metrics
        emissions = scan_results.get('codebase_emissions', 0)
        report.append(f"**Estimated Carbon Impact:** {emissions:.9f} kg CO2")

        return "\n".join(report)
