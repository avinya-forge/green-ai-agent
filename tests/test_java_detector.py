import pytest
from src.core.detectors.java_detector import JavaASTDetector

class TestJavaASTDetector:

    def test_excessive_logging(self):
        code = """
        public class Test {
            public void log() {
                System.out.println("Hello World");
            }
        }
        """
        detector = JavaASTDetector(code, "Test.java")
        violations = detector.detect_all()

        logging_violations = [v for v in violations if v['id'] == 'excessive_logging']
        assert len(logging_violations) == 1
        assert logging_violations[0]['line'] == 4

    def test_blocking_io(self):
        code = """
        public class Test {
            public void wait() {
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {}
            }
        }
        """
        detector = JavaASTDetector(code, "Test.java")
        violations = detector.detect_all()

        # It might also detect empty block for catch block depending on implementation
        # Let's check specifically for blocking_io
        blocking_violations = [v for v in violations if v['id'] == 'blocking_io']
        assert len(blocking_violations) == 1
        assert blocking_violations[0]['line'] == 5

    def test_blocking_io_fq(self):
        code = """
        public class Test {
            public void wait() {
                try {
                    java.lang.Thread.sleep(1000);
                } catch (InterruptedException e) {}
            }
        }
        """
        detector = JavaASTDetector(code, "Test.java")
        violations = detector.detect_all()

        blocking_violations = [v for v in violations if v['id'] == 'blocking_io']
        assert len(blocking_violations) == 1
        assert blocking_violations[0]['line'] == 5

    def test_string_concatenation_in_loop(self):
        code = """
        public class Test {
            public void concat() {
                String s = "";
                for (int i = 0; i < 10; i++) {
                    s += "a";
                }
            }
        }
        """
        detector = JavaASTDetector(code, "Test.java")
        violations = detector.detect_all()

        concat_violations = [v for v in violations if v['id'] == 'string_concatenation_in_loop']
        assert len(concat_violations) == 1
        assert concat_violations[0]['line'] == 6

    def test_empty_block(self):
        code = """
        public class Test {
            public void empty() {
                if (true) {
                }
            }
        }
        """
        detector = JavaASTDetector(code, "Test.java")
        violations = detector.detect_all()

        empty_violations = [v for v in violations if v['id'] == 'empty_block']
        assert len(empty_violations) == 1
        assert empty_violations[0]['line'] == 4
