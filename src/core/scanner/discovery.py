from pathlib import Path
import fnmatch
from typing import List
from src.utils.logger import logger
from src.core.config import ConfigLoader


class FileDiscoverer:
    """Helper class to discover files for scanning."""

    def __init__(self, config_loader: ConfigLoader):
        self.config_loader = config_loader

    def get_files(self, scan_path: str) -> List[str]:
        """
        Get all files to scan, respecting ignore patterns from config.

        Uses pathlib for efficiency and correct cross-platform path handling.
        """
        path = Path(scan_path)
        if path.is_file():
            return [str(path)]

        ignore_patterns = self.config_loader.get_ignored_files()
        all_files = []

        logger.info(
            f"Discovering files in {scan_path} "
            f"(Ignoring: {', '.join(ignore_patterns)})"
        )

        # Walk using path.glob or rglob while filtering
        # Optimization: We could use os.walk to prune directories,
        # but keeping consistent with original implementation for now
        for file in path.rglob('*'):
            if not file.is_file():
                continue

            # Check relative path against ignore patterns
            try:
                rel_path = file.relative_to(path)
            except ValueError:
                # Should not happen with rglob
                continue

            rel_str = str(rel_path).replace('\\', '/')  # Standardize for match

            is_ignored = False
            for pattern in ignore_patterns:
                # Match against filename and path parts
                if fnmatch.fnmatch(rel_str, pattern) or any(
                    fnmatch.fnmatch(part, pattern) for part in rel_path.parts
                ):
                    is_ignored = True
                    break

            if not is_ignored:
                all_files.append(str(file))

        logger.info(f"Found {len(all_files)} files to scan.")
        return all_files
