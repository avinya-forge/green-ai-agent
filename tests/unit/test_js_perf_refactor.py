import pytest
from src.core.detectors.javascript_detector import JavaScriptASTDetector

def test_js_combined_rules():
    code = """
    console.log("hello");
    console.time("timer");
    console.timeEnd("timer");
    eval("x=1");
    document.write("unsafe");
    var x = element.innerHTML;
    element.innerHTML = "<div></div>";
    var data = fs.readFileSync("file.txt");
    """
    detector = JavaScriptASTDetector(code, "test.js")
    violations = detector.detect_all()

    # Check console.log (excessive_console_logging)
    logs = [v for v in violations if v['id'] == 'excessive_console_logging']
    assert len(logs) == 1

    # Check console.time (console_time)
    timers = [v for v in violations if v['id'] == 'console_time']
    assert len(timers) == 2  # time and timeEnd

    # Check eval (eval_usage)
    evals = [v for v in violations if v['id'] == 'eval_usage']
    assert len(evals) == 1

    # Check document.write (document_write)
    doc_writes = [v for v in violations if v['id'] == 'document_write']
    assert len(doc_writes) == 1

    # Check innerHTML (inner_html)
    inner_htmls = [v for v in violations if v['id'] == 'inner_html']
    assert len(inner_htmls) == 1
    # Note: innerHTML read (var x = ...) is not flagged by the current rule, only assignment.

    # Check readFileSync (synchronous_io)
    sync_ios = [v for v in violations if v['id'] == 'synchronous_io']
    assert len(sync_ios) == 1

def test_js_deprecated_apis():
    code = """
    require('moment');
    import moment from 'moment';
    """
    detector = JavaScriptASTDetector(code, "test.js")
    violations = detector.detect_all()

    moments = [v for v in violations if v['id'] == 'momentjs_deprecated']
    assert len(moments) == 2

def test_js_inefficient_apis():
    code = """
    setInterval(func, 1000);
    alert("hi");
    window.confirm("sure?");
    """
    detector = JavaScriptASTDetector(code, "test.js")
    violations = detector.detect_all()

    intervals = [v for v in violations if v['id'] == 'setInterval_animation']
    assert len(intervals) == 1

    alerts = [v for v in violations if v['id'] == 'alert_usage']
    assert len(alerts) == 2
