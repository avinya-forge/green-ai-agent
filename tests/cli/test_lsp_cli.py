import unittest
from unittest.mock import patch
from click.testing import CliRunner
from src.cli.commands.lsp import lsp

class TestLSPCli(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @patch('src.cli.commands.lsp.server.start_io')
    def test_lsp_stdio(self, mock_start_io):
        result = self.runner.invoke(lsp, [])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Starting Green AI LSP server on stdio", result.output)
        mock_start_io.assert_called_once()

    @patch('src.cli.commands.lsp.server.start_tcp')
    def test_lsp_tcp(self, mock_start_tcp):
        result = self.runner.invoke(lsp, ['--tcp'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Starting Green AI LSP server on tcp://127.0.0.1:2087", result.output)
        mock_start_tcp.assert_called_once_with('127.0.0.1', 2087)

    @patch('src.cli.commands.lsp.server.start_tcp')
    def test_lsp_tcp_custom_host_port(self, mock_start_tcp):
        result = self.runner.invoke(lsp, ['--tcp', '--host', '0.0.0.0', '--port', '8080'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Starting Green AI LSP server on tcp://0.0.0.0:8080", result.output)
        mock_start_tcp.assert_called_once_with('0.0.0.0', 8080)

if __name__ == '__main__':
    unittest.main()
