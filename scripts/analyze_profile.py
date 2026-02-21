import pstats
import sys
from pathlib import Path

def analyze_profile(stats_file):
    if not Path(stats_file).exists():
        print(f"Error: Stats file {stats_file} not found.")
        return

    p = pstats.Stats(stats_file)
    p.strip_dirs()

    print("=== Top 20 by Cumulative Time ===")
    p.sort_stats('cumtime').print_stats(20)

    print("\n=== Top 20 by Total Time (Self Time) ===")
    p.sort_stats('tottime').print_stats(20)

    print("\n=== Top 20 by Call Count ===")
    p.sort_stats('ncalls').print_stats(20)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_profile.py <stats_file>")
        sys.exit(1)

    analyze_profile(sys.argv[1])
