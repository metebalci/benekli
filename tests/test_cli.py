import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock
from benekli.benekli import CommandOptions, run

class TestCommandLineInterface(unittest.TestCase):
    """Test the command-line interface functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_input = os.path.join(self.temp_dir.name, "input.tif")
        self.test_output = os.path.join(self.temp_dir.name, "output.tif")
        self.test_de = os.path.join(self.temp_dir.name, "de.tif")
        
        with open(self.test_input, "w") as f:
            f.write("")

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    @patch('benekli.benekli.run_with_opts')
    @patch('argparse.ArgumentParser.parse_args')
    def test_o_required_or_q_required(self, mock_parse_args, mock_run_with_opts):
        """Test that either -o or -q is required."""
        mock_args = MagicMock()
        mock_args.input_image = self.test_input
        mock_args.simulated_profile = "test_profile.icc"
        mock_args.rendering_intent = "p"
        mock_args.output_image = None
        mock_args.output_de = None
        mock_args.verbose = 0
        mock_parse_args.return_value = mock_args
        
        with self.assertRaises(SystemExit):
            run()
        
        mock_args.output_image = self.test_output
        mock_args.output_de = None
        mock_parse_args.return_value = mock_args
        
        run()
        mock_run_with_opts.assert_called_once()
        mock_run_with_opts.reset_mock()
        
        mock_args.output_image = None
        mock_args.output_de = self.test_de
        mock_parse_args.return_value = mock_args
        
        run()
        mock_run_with_opts.assert_called_once()
        mock_run_with_opts.reset_mock()
        
        mock_args.output_image = self.test_output
        mock_args.output_de = self.test_de
        mock_parse_args.return_value = mock_args
        
        run()
        mock_run_with_opts.assert_called_once()

    @patch('benekli.benekli.CommandOptions.load_from_args')
    def test_command_options_output_handling(self, mock_load_from_args):
        """Test that CommandOptions handles output options correctly."""
        opts = CommandOptions()
        opts.output_filename = self.test_output
        opts.de_filename = None
        
        self.assertIsNotNone(opts.output_filename)
        self.assertIsNone(opts.de_filename)
        
        opts = CommandOptions()
        opts.output_filename = None
        opts.de_filename = self.test_de
        
        self.assertIsNone(opts.output_filename)
        self.assertIsNotNone(opts.de_filename)
        
        opts = CommandOptions()
        opts.output_filename = self.test_output
        opts.de_filename = self.test_de
        
        self.assertIsNotNone(opts.output_filename)
        self.assertIsNotNone(opts.de_filename)

if __name__ == '__main__':
    unittest.main()
