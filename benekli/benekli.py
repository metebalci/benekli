import argparse
import io
import logging
import math
import os
import sys

from PIL import Image, ImageCms

from .formulas import nXYZ_to_PCSXYZ, PCSXYZ_to_nXYZ
from .formulas import XYZ_to_xyY, xyY_to_XYZ
from .formulas import XYZ_to_Lab, Lab_to_XYZ
from .formulas import Lab_to_LCh, LCh_to_Lab

logger = logging.getLogger(__name__)

# name => (cie 1931 2 deg: x, y) (cie 1964 10 deg: x, y) (cct)]
standard_illuminants = {
    # A=incandescent/tungsten
    "A":   [(0.44758, 0.40745), (0.45117, 0.40594), 2856],
    # D50=horizon light, ICC profile PCS
    "D50": [(0.34567, 0.35850), (0.34773, 0.35962), 5003],
    # D65=noon daylight, television/sRGB color space
    "D65": [(0.31272, 0.32903), (0.31382, 0.33100), 6504]
}

def linear_scale(a_tuple, scale_factor):
    return (scale_factor*a_tuple[0], scale_factor*a_tuple[1], scale_factor*a_tuple[2])

# ICC.1:2010 3.1.21 PCS illuminant
# CIE illuminant D50
PCS_illuminant_nXYZ = (0.9642, 1.0, 0.8249)
PCS_illuminant_XYZ = linear_scale(PCS_illuminant_nXYZ, 100.0)


def err(s):
    logger.error(s)
    sys.exit(1)


class CommandOptions:

    def __init__(self):
        self.color_difference_formula = "cie76",
        self.color_difference_output_filename = None
        self.display_profile_filename = None
        self.input_filename = None
        self.input_profile_filename = None
        self.no_bpc = False
        self.output_filename = None
        self.rendering_intent = "p"
        self.printer_profile_filename = None

    def load_from_args(self, args):
        self.color_difference_formula = args.color_difference_formula
        self.color_difference_output_filename = args.output_color_difference
        self.display_profile_filename = args.display_profile
        self.input_filename = args.input_image
        self.input_profile_filename = args.input_profile
        self.no_bpc = args.no_bpc
        self.output_filename = args.output_image
        self.printer_profile_filename = args.printer_profile

    def get_color_difference_formula(self):
        if self.color_difference_formula == "cie76":
            pass

        elif self.color_difference_formula == "cmc84":
            pass

        elif self.color_difference_formula == "cie94":
            pass

        elif self.color_difference_formula == "ciede2000":
            pass

        else:
            err("invalid color_difference_formula: %s" % self.color_difference_formula)

    def get_rendering_intent(self):
        if self.rendering_intent == "p":
            return ImageCms.Intent.PERCEPTUAL
        elif self.rendering_intent == "s":
            return ImageCms.Intent.SATURATION
        elif self.rendering_intent == "r":
            return ImageCms.Intent.RELATIVE_COLORIMETRIC
        elif self.rendering_intent == "a":
            return ImageCms.Intent.ABSOLUTE_COLORIMETRIC
        else:
            err("invalid rendering_intent: %s" % self.rendering_intent)

def debug_profile(profile):
    logger.debug(profile.version)
    logger.debug(profile.device_class)
    logger.debug(profile.profile_description.strip())
    logger.debug("media white point: %s" % str(profile.media_white_point))
    if profile.device_class == "mntr":
        logger.debug("%s -> %s" % (profile.xcolor_space.strip(),
                                   profile.connection_space.strip()))
    elif profile.device_class == "prtr":
        logger.debug("%s -> %s" % (profile.connection_space.strip(),
                                   profile.xcolor_space.strip()))
    else:
        err("profile device class is not mntr or prtr")

    logger.debug(str(profile.chromatic_adaptation))

def run_with_opts(opts:CommandOptions):
    with Image.open(opts.input_filename) as input_image:
        if input_image is None:
            err("cannot open input image %s" % opts.input_filename)

        if (input_image.mode != "RGB"):
            err("input image mode is not RGB")

        image_cms_profile = None
        if opts.input_profile_filename is None and "icc_profile" in input_image.info:
            logger.info("using the embedded profile in %s" % opts.input_filename)
            image_cms_profile = ImageCms.ImageCmsProfile(
                io.BytesIO(input_image.info["icc_profile"]))
            if image_cms_profile is None:
                err("cannot open embedded input profile in %s" % opts.input_filename)

        else:
            if opts.input_profile_filename is None:
                err("ERROR: image has no embedded profile and image profile is not given")

            else:
                logger.info("using the given profile %s" % opts.input_profile_filename)
                image_cms_profile = ImageCms.ImageCmsProfile(
                    opts.input_profile_filename)

                if image_cms_profile is None:
                    err("cannot open given input profile %s" % opts.input_profile_filename)

        image_profile = image_cms_profile.profile
        logger.debug("--- image profile starts ---")
        debug_profile(image_profile)
        logger.debug("--- image profile ends ---")
        logger.info("image profile: %s" % image_profile.profile_description.strip())

        if image_profile.device_class != "mntr":
            err("image profile class is not Display (mntr)")

        if image_profile.xcolor_space.strip() != "RGB":
            err("image profile xcolor space is not RGB")

        image_white_point_nXYZ = image_profile.media_white_point[0]
        logger.debug("image white point: %s" % str(image_white_point_nXYZ))

        printer_cms_profile = ImageCms.ImageCmsProfile(opts.printer_profile_filename)
        if printer_cms_profile is None:
            err("cannot open printer profile %s" % opts.printer_profile_filename)

        printer_profile = printer_cms_profile.profile

        logger.debug("--- printer profile starts ---")
        debug_profile(printer_profile)
        logger.debug("--- printer profile ends ---")
        logger.info("printer profile: %s" % printer_profile.profile_description.strip())

        if printer_profile.device_class != "prtr":
            err("printer profile class is not Output (prtr)")

        if printer_profile.xcolor_space.strip() != "RGB":
            err("printer profile xcolor space is not RGB")

        if not ImageCms.isIntentSupported(printer_profile,
                                          opts.get_rendering_intent(),
                                          ImageCms.Direction.PROOF):
            err("printer profile does not support requested rendering intent")

        printer_white_point_nXYZ = printer_profile.media_white_point[0]
        logger.debug("printer white point: %s" % str(printer_white_point_nXYZ))

        display_cms_profile = None
        if opts.display_profile_filename is None:
            display_cms_profile = ImageCms.get_display_profile()
            if display_cms_profile is None:
                err("cannot fetch the profile of the current display device, please provide it explicitly")

        else:
            display_cms_profile = ImageCms.ImageCmsProfile(opts.display_profile_filename)
            if display_cms_profile is None:
                err("cannot open display profile %s" % opts.display_profile_filename)

        display_profile = display_cms_profile.profile

        logger.debug("--- display profile starts ---")
        debug_profile(display_profile)
        logger.debug("--- display profile ends ---")
        logger.info("display profile: %s" % display_profile.profile_description.strip())

        if not ImageCms.isIntentSupported(display_profile,
                                          ImageCms.Intent.ABSOLUTE_COLORIMETRIC,
                                          ImageCms.Direction.OUTPUT):
            err("display profile does not support Absolute Colorimetric intent")

        cms_transform = ImageCms.buildProofTransform(
            inputProfile = image_profile,
            outputProfile = display_profile,
            proofProfile = printer_profile,
            inMode = "RGB",
            outMode = "RGB",
            renderingIntent = ImageCms.Intent.ABSOLUTE_COLORIMETRIC,
            proofRenderingIntent = opts.get_rendering_intent(),
            flags = ((ImageCms.Flags.SOFTPROOFING) |
                     (0 if opts.no_bpc else ImageCms.Flags.BLACKPOINTCOMPENSATION)))

        print("processing color transform...")

        output_image = cms_transform.point(input_image)
        output_filename = opts.output_filename
        if output_filename is None:
            base, ext = os.path.splitext(opts.input_filename)
            output_filename = "%s.proof%s" % (base, ext)
        output_image.save(output_filename)
        print("soft proof generated: %s" % output_filename)

        print("calculating color difference...")

        color_difference_output_filename = opts.color_difference_output_filename
        if color_difference_output_filename is None:
            base, ext = os.path.splitext(opts.input_filename)
            color_difference_output_filename = "%s.de%s" % (base, ext)

        # colorTemp defaults
        lab_profile = ImageCms.createProfile("LAB")
        input_image_Lab = ImageCms.applyTransform(
            input_image,
            ImageCms.builtTransform(image_profile,
                                    lab_profile,
                                    "RGB", "LAB"))
        output_image_Lab = ImageCms.applyTransform(
            output_image,
            ImageCms.builtTransform(output_image.info["icc_profile"],
                                    lab_profile,
                                    "RGB", "LAB"))
        color_difference_image = opts.get_color_difference_formula()(
            input_image_lab,
            output_image_lab)
        color_difference_image.save(color_difference_output_filename)

        print("color difference generated: %s" % color_difference_output_filename)

def run():
    opts = CommandOptions()
    parser = argparse.ArgumentParser(prog="benekli")
    parser.add_argument("-d", "--display-profile",
                        help="display profile (=output profile), default is active display")
    parser.add_argument("-e", "--color-difference-formula", "--delta-e-formula",
                        choices=["cie76", "cmc84", "cie94", "ciede2000"],
                        help="select the color difference (dE) formula (default: %s)" % opts.color_difference_formula,
                        default=opts.color_difference_formula)
    parser.add_argument("-i", "--input-image",
                        required=True)
    parser.add_argument("--input-profile",
                        help="input profile to use (overrides embedded profile in input image)")
    parser.add_argument("--no-bpc",
                        help="disable black point compensation (default: false)",
                        default=False,
                        action="store_true")
    parser.add_argument("-o", "--output-image",
                        help="output image to filename (default: input-image-name.proof.input-image.extension")
    parser.add_argument("-p", "--printer-profile",
                        help="printer/paper profile (=simulated device/proof profile)",
                        required=True)
    parser.add_argument("-q", "--output-color-difference",
                        help="output color difference to filename (default: input-image-name.de.input-image.extension")
    parser.add_argument("-r", "--rendering-intent",
                        choices=["p", "r", "s", "a"],
                        help="rendering intent, p(erceptual), r(elative) colorimetric, s(aturation) or a(bsolute) calorimetric (default: %s)" % opts.rendering_intent,
                        default=opts.rendering_intent)
    parser.add_argument("-v", "--verbose",
                        help="enable verbose mode, use -vv to enable debug mode",
                        action="count",
                        default=0)

    args = parser.parse_args()

    logging_format = "%(levelname)5s:%(filename)15s: %(message)s"

    logging.basicConfig(
        filename=log_file if False else None,
        level=logging.WARNING,
        format=logging_format)

    logging_level = logging.WARNING
    if args.verbose >= 2:
        logging_level = logging.DEBUG
    elif args.verbose >= 1:
        logging_level = logging.INFO
    logging.getLogger("benekli").setLevel(logging_level)

    logger.info(args)
    opts.load_from_args(args)
    run_with_opts(opts)
    return 0


if __name__ == "__main__":
    run()
