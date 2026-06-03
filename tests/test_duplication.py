from src.core.quality.duplication import DuplicationDetector


def test_duplication_detection_basic():
    detector = DuplicationDetector(min_lines=3)

    code1 = """


def alpha():
    x = 1
    y = 2
    return x + y


def beta():
    print("hi")
"""

    code2 = """


def gamma():
    x = 1
    y = 2
    return x + y
"""

    detector.add_file("file1.py", code1)
    detector.add_file("file2.py", code2)

    dupes = detector.detect_duplicates()

    assert len(dupes) >= 1
    # Check if the duplicate block (x=1, y=2, return x+y) is found
    # It should appear in both files
    found = False
    for d in dupes:
        files = [occ['file'] for occ in d['occurrences']]
        if "file1.py" in files and "file2.py" in files:
            found = True
            break
    assert found


def test_duplication_no_duplicates():
    detector = DuplicationDetector(min_lines=3)
    detector.add_file("a.py", "line1\nline2\nline3\nline4")
    detector.add_file("b.py", "other1\nother2\nother3\nother4")
    assert len(detector.detect_duplicates()) == 0


def test_duplication_normalization():
    detector = DuplicationDetector(min_lines=2)
    # Whitespace and comments should be ignored
    code1 = "x = 1  # comment\ny = 2"
    code2 = "x = 1\ny = 2  # another"

    detector.add_file("f1.py", code1)
    detector.add_file("f2.py", code2)

    dupes = detector.detect_duplicates()
    assert len(dupes) > 0
