import unittest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from PIL import Image, ImageCms
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
        self.srgb_profile = os.path.join(self.test_data_dir, "sRGB2014.icc")
        self.adobe_profile = os.path.join(self.test_data_dir, "AdobeRGB1998.icc")

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    @patch('benekli.benekli.Image.open')
    @patch('benekli.benekli.create_de_image')
    def test_run_with_opts_output_only(self, mock_create_de_image, mock_image_open):
        """Test run_with_opts with only output_filename."""
        mock_input_image = MagicMock()
        mock_output_image = MagicMock()
        mock_image_open.return_value.__enter__.return_value = mock_input_image
        mock_input_image.mode = "RGB"
        mock_input_image.info = {"icc_profile": b"test_profile"}
        
        mock_transform = MagicMock()
        mock_transform.point.return_value = mock_output_image
        mock_output_image.info = {"icc_profile": b"test_profile"}
        
        opts = CommandOptions()
        opts.input_filename = self.test_input
        opts.output_filename = self.test_output
        opts.de_filename = None
        opts.rendering_intent = "p"
        opts.simulated_profile_filename = self.adobe_profile
        
        with patch('benekli.benekli.ImageCms') as mock_cms:
            mock_cms.buildProofTransform.return_value = mock_transform
            mock_cms.ImageCmsProfile.return_value = MagicMock()
            mock_cms.ImageCmsProfile.return_value.profile = MagicMock()
            mock_cms.ImageCmsProfile.return_value.profile.device_class = "prtr"
            mock_cms.ImageCmsProfile.return_value.profile.xcolor_space = MagicMock()
            mock_cms.ImageCmsProfile.return_value.profile.xcolor_space.strip.return_value = "RGB"
            mock_cms.ImageCmsProfile.return_value.profile.connection_space = MagicMock()
            mock_cms.ImageCmsProfile.return_value.profile.connection_space.strip.return_value = "XYZ"
            mock_cms.ImageCmsProfile.return_value.profile.media_white_point = [(1.0, 1.0, 1.0)]
            mock_cms.ImageCmsProfile.return_value.profile.profile_description = "Test Profile"
            mock_cms.isIntentSupported.return_value = True
            mock_cms.Intent.PERCEPTUAL = 0
            mock_cms.Intent.SATURATION = 1
            mock_cms.Intent.RELATIVE_COLORIMETRIC = 2
            mock_cms.Intent.ABSOLUTE_COLORIMETRIC = 3
            mock_cms.Direction.PROOF = 0
            mock_cms.Direction.OUTPUT = 1
            mock_cms.Flags.SOFTPROOFING = 0x0400
            mock_cms.Flags.BLACKPOINTCOMPENSATION = 0x0100
            mock_cms.Flags.GAMUTCHECK = 0x1000
            mock_cms.get_display_profile.return_value = MagicMock()
            
            with patch('benekli.benekli.print'):  # Suppress print output
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
        mock_image_open.return_value.__enter__.return_value = mock_input_image
        mock_input_image.mode = "RGB"
        mock_input_image.info = {"icc_profile": b"test_profile"}
        mock_create_de_image.return_value = mock_de_image
        
        mock_transform = MagicMock()
        mock_transform.point.return_value = mock_output_image
        mock_output_image.info = {"icc_profile": b"test_profile"}
        
        opts = CommandOptions()
        opts.input_filename = self.test_input
        opts.output_filename = None
        opts.de_filename = self.test_de
        opts.rendering_intent = "p"
        opts.simulated_profile_filename = self.adobe_profile
        
        with patch('benekli.benekli.ImageCms') as mock_cms:
            mock_cms.buildProofTransform.return_value = mock_transform
            mock_cms.ImageCmsProfile.return_value = MagicMock()
            mock_cms.ImageCmsProfile.return_value.profile = MagicMock()
            mock_cms.ImageCmsProfile.return_value.profile.device_class = "prtr"
            mock_cms.ImageCmsProfile.return_value.profile.xcolor_space = MagicMock()
            mock_cms.ImageCmsProfile.return_value.profile.xcolor_space.strip.return_value = "RGB"
            mock_cms.ImageCmsProfile.return_value.profile.connection_space = MagicMock()
            mock_cms.ImageCmsProfile.return_value.profile.connection_space.strip.return_value = "XYZ"
            mock_cms.ImageCmsProfile.return_value.profile.media_white_point = [(1.0, 1.0, 1.0)]
            mock_cms.ImageCmsProfile.return_value.profile.profile_description = "Test Profile"
            mock_cms.isIntentSupported.return_value = True
            mock_cms.Intent.PERCEPTUAL = 0
            mock_cms.Intent.SATURATION = 1
            mock_cms.Intent.RELATIVE_COLORIMETRIC = 2
            mock_cms.Intent.ABSOLUTE_COLORIMETRIC = 3
            mock_cms.Direction.PROOF = 0
            mock_cms.Direction.OUTPUT = 1
            mock_cms.Flags.SOFTPROOFING = 0x0400
            mock_cms.Flags.BLACKPOINTCOMPENSATION = 0x0100
            mock_cms.Flags.GAMUTCHECK = 0x1000
            mock_cms.get_display_profile.return_value = MagicMock()
            mock_cms.applyTransform.return_value = MagicMock()
            mock_cms.buildTransform.return_value = MagicMock()
            mock_cms.createProfile.return_value = MagicMock()
            
            with patch('benekli.benekli.print'):  # Suppress print output
                run_with_opts(opts)
            
            self.assertEqual(mock_output_image.save.call_count, 0)
            mock_create_de_image.assert_called_once()
            mock_de_image.save.assert_called_once()

    @patch('benekli.benekli.Image.open')
    @patch('benekli.benekli.create_de_image')
    def test_run_with_opts_both(self, mock_create_de_image, mock_image_open):
        """Test run_with_opts with both output_filename and de_filename."""
        mock_input_image = MagicMock()
        mock_output_image = MagicMock()
        mock_de_image = MagicMock()
        mock_image_open.return_value.__enter__.return_value = mock_input_image
        mock_input_image.mode = "RGB"
        mock_input_image.info = {"icc_profile": b"test_profile"}
        mock_create_de_image.return_value = mock_de_image
        
        mock_transform = MagicMock()
        mock_transform.point.return_value = mock_output_image
        mock_output_image.info = {"icc_profile": b"test_profile"}
        
        opts = CommandOptions()
        opts.input_filename = self.test_input
        opts.output_filename = self.test_output
        opts.de_filename = self.test_de
        opts.rendering_intent = "p"
        opts.simulated_profile_filename = self.adobe_profile
        
        with patch('benekli.benekli.ImageCms') as mock_cms:
            mock_cms.buildProofTransform.return_value = mock_transform
            mock_cms.ImageCmsProfile.return_value = MagicMock()
            mock_cms.ImageCmsProfile.return_value.profile = MagicMock()
            mock_cms.ImageCmsProfile.return_value.profile.device_class = "prtr"
            mock_cms.ImageCmsProfile.return_value.profile.xcolor_space = MagicMock()
            mock_cms.ImageCmsProfile.return_value.profile.xcolor_space.strip.return_value = "RGB"
            mock_cms.ImageCmsProfile.return_value.profile.connection_space = MagicMock()
            mock_cms.ImageCmsProfile.return_value.profile.connection_space.strip.return_value = "XYZ"
            mock_cms.ImageCmsProfile.return_value.profile.media_white_point = [(1.0, 1.0, 1.0)]
            mock_cms.ImageCmsProfile.return_value.profile.profile_description = "Test Profile"
            mock_cms.isIntentSupported.return_value = True
            mock_cms.Intent.PERCEPTUAL = 0
            mock_cms.Intent.SATURATION = 1
            mock_cms.Intent.RELATIVE_COLORIMETRIC = 2
            mock_cms.Intent.ABSOLUTE_COLORIMETRIC = 3
            mock_cms.Direction.PROOF = 0
            mock_cms.Direction.OUTPUT = 1
            mock_cms.Flags.SOFTPROOFING = 0x0400
            mock_cms.Flags.BLACKPOINTCOMPENSATION = 0x0100
            mock_cms.Flags.GAMUTCHECK = 0x1000
            mock_cms.get_display_profile.return_value = MagicMock()
            mock_cms.applyTransform.return_value = MagicMock()
            mock_cms.buildTransform.return_value = MagicMock()
            mock_cms.createProfile.return_value = MagicMock()
            
            with patch('benekli.benekli.print'):  # Suppress print output
                run_with_opts(opts)
            
            mock_output_image.save.assert_called_once()
            mock_create_de_image.assert_called_once()
            mock_de_image.save.assert_called_once()

if __name__ == '__main__':
    unittest.main()
