import unittest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from PIL import Image
import numpy as np
from benekli.benekli import run_with_opts, CommandOptions

class TestFunctionalCLI(unittest.TestCase):
    """Functional tests for the benekli CLI."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.test_data_dir = os.path.join(self.test_dir, "test_data")
        self.test_input = os.path.join(self.test_data_dir, "FourteenBalls.tif")
        self.test_output = os.path.join(self.temp_dir.name, "output.tif")
        self.test_de = os.path.join(self.temp_dir.name, "de.tif")

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    @patch('benekli.benekli.Image.open')
    @patch('benekli.benekli.create_de_image')
    def test_run_with_opts_output_only(self, mock_create_de_image, mock_image_open):
        """Test run_with_opts with only output_filename."""
        mock_input_image = MagicMock()
        mock_output_image = MagicMock()
        mock_image_open.return_value = mock_input_image
        mock_input_image.mode = "RGB"
        
        mock_transform = MagicMock()
        mock_transform.point.return_value = mock_output_image
        
        opts = CommandOptions()
        opts.input_filename = self.test_input
        opts.output_filename = self.test_output
        opts.de_filename = None
        opts.rendering_intent = "p"
        opts.verbose = 0
        
        with patch('benekli.benekli.cms') as mock_cms:
            mock_cms.buildTransform.return_value = mock_transform
            mock_cms.getOpenProfile.return_value = MagicMock()
            
            run_with_opts(opts)
            
            mock_output_image.save.assert_called_once()
            mock_create_de_image.assert_not_called()

    @patch('benekli.benekli.Image.open')
    @patch('benekli.benekli.create_de_image')
    def test_run_with_opts_de_only(self, mock_create_de_image, mock_image_open):
        """Test run_with_opts with only de_filename."""
        mock_input_image = MagicMock()
        mock_output_image = MagicMock()
        mock_de_image = MagicMock()
        mock_image_open.return_value = mock_input_image
        mock_input_image.mode = "RGB"
        mock_create_de_image.return_value = mock_de_image
        
        mock_transform = MagicMock()
        mock_transform.point.return_value = mock_output_image
        
        opts = CommandOptions()
        opts.input_filename = self.test_input
        opts.output_filename = None
        opts.de_filename = self.test_de
        opts.rendering_intent = "p"
        opts.verbose = 0
        opts.de_formula = "cie76"
        
        with patch('benekli.benekli.cms') as mock_cms:
            mock_cms.buildTransform.return_value = mock_transform
            mock_cms.getOpenProfile.return_value = MagicMock()
            
            run_with_opts(opts)
            
            mock_output_image.save.assert_not_called()
            mock_create_de_image.assert_called_once()
            mock_de_image.save.assert_called_once()

    @patch('benekli.benekli.Image.open')
    @patch('benekli.benekli.create_de_image')
    def test_run_with_opts_both(self, mock_create_de_image, mock_image_open):
        """Test run_with_opts with both output_filename and de_filename."""
        mock_input_image = MagicMock()
        mock_output_image = MagicMock()
        mock_de_image = MagicMock()
        mock_image_open.return_value = mock_input_image
        mock_input_image.mode = "RGB"
        mock_create_de_image.return_value = mock_de_image
        
        mock_transform = MagicMock()
        mock_transform.point.return_value = mock_output_image
        
        opts = CommandOptions()
        opts.input_filename = self.test_input
        opts.output_filename = self.test_output
        opts.de_filename = self.test_de
        opts.rendering_intent = "p"
        opts.verbose = 0
        opts.de_formula = "cie76"
        
        with patch('benekli.benekli.cms') as mock_cms:
            mock_cms.buildTransform.return_value = mock_transform
            mock_cms.getOpenProfile.return_value = MagicMock()
            
            run_with_opts(opts)
            
            mock_output_image.save.assert_called_once()
            mock_create_de_image.assert_called_once()
            mock_de_image.save.assert_called_once()

if __name__ == '__main__':
    unittest.main()
