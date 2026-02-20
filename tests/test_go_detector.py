import pytest
from src.core.detectors.go_detector import GoASTDetector

class TestGoASTDetector:

    def test_formatted_print(self):
        code = """
        package main
        import "fmt"
        func main() {
            fmt.Println("Hello World")
            fmt.Printf("Number: %d", 10)
        }
        """
        detector = GoASTDetector(code, "main.go")
        violations = detector.detect_all()

        print_violations = [v for v in violations if v['id'] == 'formatted_print']
        assert len(print_violations) == 2
        assert print_violations[0]['line'] == 5
        assert print_violations[1]['line'] == 6

    def test_empty_block(self):
        code = """
        package main
        func main() {
            if true {
            }
        }
        """
        detector = GoASTDetector(code, "main.go")
        violations = detector.detect_all()

        empty_violations = [v for v in violations if v['id'] == 'empty_block']
        assert len(empty_violations) == 1
        assert empty_violations[0]['line'] == 4 # 'if true {' is line 4

    def test_infinite_loop(self):
        code = """
        package main
        func main() {
            for {
            }
        }
        """
        detector = GoASTDetector(code, "main.go")
        violations = detector.detect_all()

        # infinite_loop violation + empty_block violation
        infinite_violations = [v for v in violations if v['id'] == 'infinite_loop']
        empty_violations = [v for v in violations if v['id'] == 'empty_block']

        assert len(infinite_violations) == 1
        assert len(empty_violations) == 1
        assert infinite_violations[0]['line'] == 4

    def test_finite_loop(self):
        code = """
        package main
        func main() {
            for i := 0; i < 10; i++ {
                fmt.Println(i)
            }
        }
        """
        detector = GoASTDetector(code, "main.go")
        violations = detector.detect_all()

        infinite_violations = [v for v in violations if v['id'] == 'infinite_loop']
        assert len(infinite_violations) == 0

    def test_while_loop(self):
        # Go's "while" is just for condition {}
        code = """
        package main
        func main() {
            i := 0
            for i < 10 {
                i++
            }
        }
        """
        detector = GoASTDetector(code, "main.go")
        violations = detector.detect_all()

        infinite_violations = [v for v in violations if v['id'] == 'infinite_loop']
        assert len(infinite_violations) == 0

    def test_string_concatenation_in_loop(self):
        code = """
        package main
        func main() {
            s := ""
            for i := 0; i < 10; i++ {
                s += "a"
                s = s + "b"
            }
            s += "c" // Outside loop, should not be detected
        }
        """
        detector = GoASTDetector(code, "main.go")
        violations = detector.detect_all()

        concat_violations = [v for v in violations if v['id'] == 'string_concatenation_in_loop']
        assert len(concat_violations) == 2
        # Lines might vary based on indentation in string, but let's assume lines 6 and 7
        # Line 6: s += "a"
        # Line 7: s = s + "b"

        # Verify lines
        lines = sorted([v['line'] for v in concat_violations])
        assert lines == [6, 7]
