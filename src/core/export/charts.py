import math
import html
from typing import Dict

class ChartGenerator:
    """Generates SVG charts for reports."""

    COLORS = {
        'critical': '#e53e3e',
        'high': '#dd6b20',
        'medium': '#d69e2e',
        'low': '#3182ce',
        'info': '#805ad5',
        'default': '#cbd5e0'
    }

    @staticmethod
    def generate_pie_chart(data: Dict[str, int], title: str = "") -> str:
        """
        Generate an SVG pie chart from data.

        Args:
            data: Dictionary of label -> value
            title: Chart title

        Returns:
            SVG string
        """
        title = html.escape(title)

        total = sum(data.values())
        if total == 0:
            return ChartGenerator._generate_empty_chart(title)

        radius = 80
        center_x = 120
        center_y = 150
        start_angle = 0

        svg_parts = [
            f'<svg width="400" height="300" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">',
            f'<text x="200" y="30" text-anchor="middle" font-family="sans-serif" font-size="16" font-weight="bold" fill="#2d3748">{title}</text>'
        ]

        # Legend setup
        legend_x = 240
        legend_y = 100
        legend_step = 25

        current_legend_y = legend_y

        active_items = {k: v for k, v in data.items() if v > 0}

        if not active_items:
             return ChartGenerator._generate_empty_chart(title)

        for i, (label, value) in enumerate(active_items.items()):
            escaped_label = html.escape(label)
            percentage = value / total
            angle = percentage * 360
            end_angle = start_angle + angle

            # Calculate coordinates (0 angle is 12 o'clock)
            x1 = center_x + radius * math.cos(math.radians(start_angle - 90))
            y1 = center_y + radius * math.sin(math.radians(start_angle - 90))
            x2 = center_x + radius * math.cos(math.radians(end_angle - 90))
            y2 = center_y + radius * math.sin(math.radians(end_angle - 90))

            large_arc = 1 if angle > 180 else 0

            color = ChartGenerator.COLORS.get(label.lower(), ChartGenerator.COLORS['default'])
            if label.lower() not in ChartGenerator.COLORS:
                 fallback_colors = ['#4299e1', '#48bb78', '#ed8936', '#f56565', '#a0aec0']
                 color = fallback_colors[i % len(fallback_colors)]

            # Draw slice
            if percentage >= 0.9999: # Full circle
                path = f'<circle cx="{center_x}" cy="{center_y}" r="{radius}" fill="{color}" />'
            else:
                path = f'<path d="M {center_x} {center_y} L {x1} {y1} A {radius} {radius} 0 {large_arc} 1 {x2} {y2} Z" fill="{color}" stroke="white" stroke-width="2"/>'

            svg_parts.append(path)

            # Draw legend item
            svg_parts.append(f'<rect x="{legend_x}" y="{current_legend_y}" width="15" height="15" fill="{color}" rx="3" />')
            svg_parts.append(f'<text x="{legend_x + 25}" y="{current_legend_y + 12}" font-family="sans-serif" font-size="12" fill="#4a5568">{escaped_label} ({value})</text>')

            start_angle = end_angle
            current_legend_y += legend_step

        svg_parts.append('</svg>')
        return "\n".join(svg_parts)

    @staticmethod
    def generate_bar_chart(data: Dict[str, int], title: str = "") -> str:
        """
        Generate an SVG horizontal bar chart.

        Args:
            data: Dictionary of label -> value
            title: Chart title

        Returns:
            SVG string
        """
        title = html.escape(title)

        if not data:
             return ChartGenerator._generate_empty_chart(title)

        max_val = max(data.values()) if data else 0
        if max_val == 0:
            return ChartGenerator._generate_empty_chart(title)

        width = 400
        height = len(data) * 40 + 60
        bar_height = 20
        start_y = 60
        label_width = 180
        chart_width = width - label_width - 40 # Padding

        svg_parts = [
            f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
            f'<text x="{width/2}" y="30" text-anchor="middle" font-family="sans-serif" font-size="16" font-weight="bold" fill="#2d3748">{title}</text>'
        ]

        for i, (label, value) in enumerate(data.items()):
            escaped_label = html.escape(label)
            y = start_y + i * 40
            bar_width = (value / max_val) * chart_width

            # Label truncation
            display_label = escaped_label
            if len(display_label) > 25:
                display_label = display_label[:22] + "..."

            # Draw label
            svg_parts.append(f'<text x="{label_width - 10}" y="{y + bar_height/2 + 5}" text-anchor="end" font-family="sans-serif" font-size="11" fill="#4a5568">{display_label}</text>')

            # Draw bar
            color = "#4299e1"
            svg_parts.append(f'<rect x="{label_width}" y="{y}" width="{bar_width}" height="{bar_height}" fill="{color}" rx="3" />')

            # Draw value
            svg_parts.append(f'<text x="{label_width + bar_width + 5}" y="{y + bar_height/2 + 5}" font-family="sans-serif" font-size="11" fill="#4a5568">{value}</text>')

        svg_parts.append('</svg>')
        return "\n".join(svg_parts)

    @staticmethod
    def _generate_empty_chart(title: str) -> str:
        return f'<svg width="400" height="200" viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg"><text x="200" y="30" text-anchor="middle" font-family="sans-serif" font-size="16" font-weight="bold" fill="#2d3748">{title}</text><text x="200" y="100" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#a0aec0">No Data Available</text></svg>'
