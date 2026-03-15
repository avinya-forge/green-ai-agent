import html
import io
import base64
from typing import Dict
import matplotlib
import matplotlib.pyplot as plt

# Use non-interactive backend for static image generation
matplotlib.use('Agg')


class ChartGenerator:
    """Generates static image charts (base64 PNG) for reports."""

    COLORS = {
        'critical': '#e53e3e',
        'high': '#dd6b20',
        'medium': '#d69e2e',
        'low': '#3182ce',
        'info': '#805ad5',
        'default': '#cbd5e0'
    }

    @staticmethod
    def _generate_empty_chart(title: str) -> str:
        fig, ax = plt.subplots(figsize=(4, 2))
        fig.patch.set_facecolor('white')
        ax.set_title(title, fontsize=12, fontweight='bold', color='#2d3748', pad=10)
        ax.text(0.5, 0.5, 'No Data Available', horizontalalignment='center',
                verticalalignment='center', fontsize=10, color='#a0aec0')
        ax.axis('off')

        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', transparent=False)
        plt.close(fig)
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode('utf-8')
        return f'<img src="data:image/png;base64,{img_b64}" alt="{html.escape(title)}" style="max-width:100%; height:auto;"/>'

    @staticmethod
    def generate_pie_chart(data: Dict[str, int], title: str = "") -> str:
        """
        Generate a static PNG pie chart from data.

        Args:
            data: Dictionary of label -> value
            title: Chart title

        Returns:
            HTML img tag string with base64 encoded PNG
        """
        active_items = {k: v for k, v in data.items() if v > 0}
        total = sum(active_items.values())
        if total == 0 or not active_items:
            return ChartGenerator._generate_empty_chart(title)

        labels = []
        sizes = []
        colors = []
        fallback_colors = ['#4299e1', '#48bb78', '#ed8936', '#f56565', '#a0aec0']

        for i, (label, value) in enumerate(active_items.items()):
            labels.append(f"{label} ({value})")
            sizes.append(value)

            c = ChartGenerator.COLORS.get(label.lower(), ChartGenerator.COLORS['default'])
            if label.lower() not in ChartGenerator.COLORS:
                c = fallback_colors[i % len(fallback_colors)]
            colors.append(c)

        fig, ax = plt.subplots(figsize=(5, 3.5))
        fig.patch.set_facecolor('white')

        # Plot pie chart
        wedges, texts = ax.pie(sizes, colors=colors, startangle=90,
                               wedgeprops=dict(width=0.4, edgecolor='w'))

        ax.set_title(title, fontsize=14, fontweight='bold', color='#2d3748', pad=15)

        # Add legend
        ax.legend(wedges, labels,
                  title="",
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1),
                  frameon=False,
                  prop={'size': 10})

        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', transparent=False)
        plt.close(fig)
        buf.seek(0)

        img_b64 = base64.b64encode(buf.read()).decode('utf-8')
        return f'<img src="data:image/png;base64,{img_b64}" alt="{html.escape(title)}" style="max-width:100%; height:auto;"/>'

    @staticmethod
    def generate_bar_chart(data: Dict[str, int], title: str = "") -> str:
        """
        Generate a static PNG horizontal bar chart.

        Args:
            data: Dictionary of label -> value
            title: Chart title

        Returns:
            HTML img tag string with base64 encoded PNG
        """
        if not data:
            return ChartGenerator._generate_empty_chart(title)

        max_val = max(data.values()) if data else 0
        if max_val == 0:
            return ChartGenerator._generate_empty_chart(title)

        # Truncate labels for better display
        labels = []
        for lbl in data.keys():
            if len(lbl) > 25:
                labels.append(lbl[:22] + "...")
            else:
                labels.append(lbl)

        values = list(data.values())

        # Calculate figure height dynamically based on number of items
        # Minimum height of 2, plus 0.4 per item
        fig_height = max(2.5, len(data) * 0.4 + 1.5)

        fig, ax = plt.subplots(figsize=(6, fig_height))
        fig.patch.set_facecolor('white')

        y_pos = range(len(labels))

        # Plot horizontal bars
        bars = ax.barh(y_pos, values, color='#4299e1', height=0.6)

        # Invert y-axis to have the first item at the top
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=10, color='#4a5568')
        ax.invert_yaxis()

        ax.set_title(title, fontsize=14, fontweight='bold', color='#2d3748', pad=15)

        # Remove spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        # Remove x-axis ticks
        ax.xaxis.set_ticks_position('none')
        ax.set_xticklabels([])

        # Add value labels to the end of each bar
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + (max_val * 0.02), bar.get_y() + bar.get_height() / 2,
                    f'{values[i]}',
                    ha='left', va='center', fontsize=10, color='#4a5568')

        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', transparent=False)
        plt.close(fig)
        buf.seek(0)

        img_b64 = base64.b64encode(buf.read()).decode('utf-8')
        return f'<img src="data:image/png;base64,{img_b64}" alt="{html.escape(title)}" style="max-width:100%; height:auto;"/>'
