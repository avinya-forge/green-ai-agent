"""
Code duplication detection for Green AI.
Implements Type-1 (exact match) detection using rolling hash.
"""

import hashlib
from typing import List, Dict, Tuple


class DuplicationDetector:
    """
    Detects duplicate code blocks across multiple files.
    Focuses on Type-1 duplication (exact string match ignoring whitespace/comments).
    """

    def __init__(self, min_lines: int = 5):
        self.min_lines = min_lines
        # Map of hash -> list of (file_path, start_line, end_line)
        self.hashes: Dict[str, List[Tuple[str, int, int]]] = {}

    def _normalize_line(self, line: str) -> str:
        """Remove whitespace and comments for comparison."""
        line = line.strip()
        if '#' in line:
            line = line.split('#')[0].strip()
        elif '//' in line:
            line = line.split('//')[0].strip()
        return line

    def add_file(self, file_path: str, content: str):
        """Analyze a file and record hashes of its blocks."""
        lines = content.split('\n')
        normalized_lines = [self._normalize_line(line) for line in lines]

        # Using a sliding window of min_lines
        for i in range(len(normalized_lines) - self.min_lines + 1):
            block = "".join(normalized_lines[i:i + self.min_lines])
            if not block:
                continue

            block_hash = hashlib.md5(block.encode('utf-8')).hexdigest()

            if block_hash not in self.hashes:
                self.hashes[block_hash] = []

            self.hashes[block_hash].append((file_path, i + 1, i + self.min_lines))

    def detect_duplicates(self) -> List[Dict]:
        """
        Return a list of detected duplicate blocks.
        Only returns hashes with more than one occurrence.
        """
        duplicates = []
        for block_hash, occurrences in self.hashes.items():
            if len(occurrences) > 1:
                # Merge overlapping or contiguous blocks from the same file if needed
                # For MVP, we just report the duplicate sets
                duplicates.append({
                    'hash': block_hash,
                    'occurrences': [
                        {'file': occ[0], 'start': occ[1], 'end': occ[2]}
                        for occ in occurrences
                    ],
                    'count': len(occurrences)
                })
        return duplicates

# Type-2 (structural) detection planned for Phase 5.
# Currently supporting Type-1 (exact match) with normalization.
