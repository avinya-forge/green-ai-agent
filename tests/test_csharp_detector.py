import pytest
from src.core.detectors.csharp_detector import CSharpASTDetector

class TestCSharpASTDetector:

    def test_empty_block(self):
        code = """
        using System;

        namespace Example
        {
            class Program
            {
                static void Main(string[] args)
                {
                    if (true)
                    {
                    }
                }
            }
        }
        """
        detector = CSharpASTDetector(code, "Program.cs")
        violations = detector.detect_all()

        empty_violations = [v for v in violations if v['id'] == 'empty_block']
        assert len(empty_violations) == 1
        assert empty_violations[0]['line'] == 11

    def test_blocking_async_calls(self):
        code = """
        using System;
        using System.Threading.Tasks;

        class Program
        {
            static void Main()
            {
                var task = DoWorkAsync();
                task.Wait();
                var result = task.Result;
            }

            static async Task<int> DoWorkAsync()
            {
                await Task.Delay(100);
                return 42;
            }
        }
        """
        detector = CSharpASTDetector(code, "Program.cs")
        violations = detector.detect_all()

        blocking_violations = [v for v in violations if v['id'] == 'blocking_async_calls']
        assert len(blocking_violations) == 2
        # `task.Wait();` is line 10, `task.Result;` is line 11
        lines = sorted([v['line'] for v in blocking_violations])
        assert lines == [10, 11]

    def test_string_concatenation_in_loop(self):
        code = """
        using System;

        class Program
        {
            static void Main()
            {
                string s = "";
                for (int i = 0; i < 10; i++)
                {
                    s += i.ToString();
                }
            }
        }
        """
        detector = CSharpASTDetector(code, "Program.cs")
        violations = detector.detect_all()

        concat_violations = [v for v in violations if v['id'] == 'string_concatenation_in_loop']
        assert len(concat_violations) == 1
        assert concat_violations[0]['line'] == 9

    def test_multiple_linq_iterations(self):
        code = """
        using System;
        using System.Linq;
        using System.Collections.Generic;

        class Program
        {
            static void Main()
            {
                var list = new List<int> { 1, 2, 3 };
                var query = list.Where(x => x > 1);

                foreach (var item in list)
                {
                    var materialized = query.ToList();
                }
            }
        }
        """
        detector = CSharpASTDetector(code, "Program.cs")
        violations = detector.detect_all()

        linq_violations = [v for v in violations if v['id'] == 'multiple_linq_iterations']
        assert len(linq_violations) == 1
        assert linq_violations[0]['line'] == 13
