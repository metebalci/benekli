# SPDX-FileCopyrightText: 2025 Mete Balci
#
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import io
import logging
import sys
from typing import Callable

from PIL import Image, ImageCms

from .constants import PCS_illuminant_nXYZ
from .formulas import ColorTriple
from .formulas import nXYZ_to_PCSXYZ, PCSXYZ_to_nXYZ
from .formulas import XYZ_to_xyY, xyY_to_XYZ
from .formulas import XYZ_to_Lab, Lab_to_XYZ
from .formulas import Lab_to_LCh, LCh_to_Lab
from .formulas import de76, de94_for_graphic_arts, de94_for_textiles, de2000

logger = logging.getLogger(__name__)


def err(s):
    logger.error(s)
    sys.exit(1)


class CommandOptions:

    def __init__(self):
        self.de_formula = "cie76"
        self.de_filename = None
        self.display_profile_filename = None
        self.input_filename = None
        self.input_profile_filename = None
        self.no_bpc = False
        self.no_gamut_check = False
        self.output_filename = None
        self.rendering_intent = "p"
        self.simulated_profile_filename = None

    def load_from_args(self, args):
        self.de_formula = args.de_formula
        self.de_filename = args.output_de
        self.display_profile_filename = args.display_profile
        self.input_filename = args.input_image
        self.input_profile_filename = args.input_profile
        self.no_bpc = args.no_bpc
        self.no_gamut_check = args.no_gamut_check
        self.output_filename = args.output_image
        self.rendering_intent = args.rendering_intent
        self.simulated_profile_filename = args.simulated_profile

    def get_color_difference_formula(self):
        if self.de_formula == "cie76":
            return de76

        elif self.de_formula == "cie94":
            return de94_for_graphic_arts

        elif self.de_formula == "ciede2000":
            return de2000

        else:
            err("invalid de_formula: %s" % self.de_formula)

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

    # for monitor/display/input image profiles
    if profile.device_class == "mntr":
        # since it is input, device space -> connection space
        logger.debug(
            "%s -> %s"
            % (profile.xcolor_space.strip(), profile.connection_space.strip())
        )

    # printer/output profiles
    elif profile.device_class == "prtr":
        # since it is output, connection space -> device space
        logger.debug(
            "%s -> %s"
            % (profile.connection_space.strip(), profile.xcolor_space.strip())
        )

    # abstract profiles e.g. LAB
    elif profile.device_class == "abst":
        # it is abstract, device space -> connection space
        logger.debug(
            "%s -> %s"
            % (profile.xcolor_space.strip(), profile.connection_space.strip())
        )

    else:
        err(
            "profile device class is none of mntr, prtr or abst but %s"
            % profile.device_class
        )

    logger.debug(str(profile.chromatic_adaptation))


def de_colorizer(de):
    demin = 3.0
    demax = 8.0
    # green
    if de <= 1.0:
        return [0, 0xFF, 0]

    # yellow
    elif de <= 2.0:
        return [0xFF, 0xFF, 0]

    # orange
    elif de <= demin:
        return [0xFF, 0x45, 0]

    # red gradient from demin to demax
    else:
        if de > demax:
            de = demax
        start_at_red = 140
        gradient = start_at_red - ((de - demin) / (demax - demin)) * start_at_red
        return [0xFF, gradient, gradient]


def create_de_image(
    de_formula: Callable[[ColorTriple, ColorTriple], float], im1: Image, im2: Image
) -> Image:
    assert im1.mode == "LAB"
    assert im2.mode == "LAB"
    assert im1.size == im2.size
    data1 = im1.getdata()
    data2 = im2.getdata()
    for i in range(0, im1.width * im1.height):
        Lab1 = data1[i]
        Lab2 = data2[i]
        de = de_formula(Lab1, Lab2)
        out[y, x] = de_colorizer(de)
    return Image.fromarray(out, mode="RGB")


def run_with_opts(opts: CommandOptions):
    with Image.open(opts.input_filename) as input_image:
        if input_image is None:
            err("cannot open input image %s" % opts.input_filename)

        lab_profile = ImageCms.createProfile("LAB")

        if input_image.mode == "LAB":
            logger.info("input image is Lab")

        elif input_image.mode == "RGB":
            logger.info("input image is RGB")

        else:
            err("input image is neither RGB nor Lab")

        image_cms_profile = None
        if opts.input_profile_filename is None:
            if "icc_profile" in input_image.info:
                logger.info("using the embedded profile in %s" % opts.input_filename)
                image_cms_profile = ImageCms.ImageCmsProfile(
                    io.BytesIO(input_image.info["icc_profile"])
                )
                if image_cms_profile is None:
                    err(
                        "cannot open embedded input profile in %s" % opts.input_filename
                    )

            elif input_image.mode == "LAB":
                # if there is no embedded profile, but the image is in Lab space
                # then built-in/standard/abstract Lab profile can be used
                # since it is an identity transform only
                image_cms_profile = ImageCms.ImageCmsProfile(lab_profile)
                assert image_cms_profile is not None

            else:
                err("image is RGB and does not have an embedded profile")

        else:
            logger.info("using the given profile %s" % opts.input_profile_filename)
            image_cms_profile = ImageCms.ImageCmsProfile(opts.input_profile_filename)
            if image_cms_profile is None:
                err("cannot open given input profile %s" % opts.input_profile_filename)

        image_profile = image_cms_profile.profile
        logger.debug("--- image profile starts ---")
        debug_profile(image_profile)
        logger.debug("--- image profile ends ---")
        logger.info("image profile: %s" % image_profile.profile_description.strip())

        if input_image.mode == "RGB" and image_profile.device_class != "mntr":
            err(
                "input image is RGB and but image profile device class is not Display (mntr) but %s"
                % image_profile.device_class
            )

        if input_image.mode == "RGB" and image_profile.xcolor_space.strip() != "RGB":
            err("input image is RGB but the profile xcolor space is not RGB")

        if input_image.mode == "LAB" and image_profile.xcolor_space.strip() != "Lab":
            err("input image is Lab but the profile xcolor space is not Lab")

        image_white_point_nXYZ = image_profile.media_white_point[0]
        logger.debug("image white point: %s" % str(image_white_point_nXYZ))

        simulated_cms_profile = ImageCms.ImageCmsProfile(
            opts.simulated_profile_filename
        )
        if simulated_cms_profile is None:
            err("cannot open simulated profile %s" % opts.simulated_profile_filename)

        simulated_profile = simulated_cms_profile.profile

        logger.debug("--- simulated profile starts ---")
        debug_profile(simulated_profile)
        logger.debug("--- simulated profile ends ---")
        logger.info(
            "simulated profile: %s" % simulated_profile.profile_description.strip()
        )

        if simulated_profile.device_class != "prtr":
            err("simulated profile class is not Output (prtr)")

        if simulated_profile.xcolor_space.strip() != "RGB":
            err("simulated profile xcolor space is not RGB")

        if not ImageCms.isIntentSupported(
            simulated_profile, opts.get_rendering_intent(), ImageCms.Direction.PROOF
        ):
            err("simulated profile does not support requested rendering intent")

        simulated_white_point_nXYZ = simulated_profile.media_white_point[0]
        logger.debug("simulated white point: %s" % str(simulated_white_point_nXYZ))

        display_cms_profile = None
        if opts.display_profile_filename is None:
            display_cms_profile = ImageCms.get_display_profile()
            if display_cms_profile is None:
                err(
                    "cannot fetch the profile of the current display device, please provide it explicitly"
                )

        else:
            display_cms_profile = ImageCms.ImageCmsProfile(
                opts.display_profile_filename
            )
            if display_cms_profile is None:
                err("cannot open display profile %s" % opts.display_profile_filename)

        display_profile = display_cms_profile.profile

        logger.debug("--- display profile starts ---")
        debug_profile(display_profile)
        logger.debug("--- display profile ends ---")
        logger.info("display profile: %s" % display_profile.profile_description.strip())

        if not ImageCms.isIntentSupported(
            display_profile,
            ImageCms.Intent.ABSOLUTE_COLORIMETRIC,
            ImageCms.Direction.OUTPUT,
        ):
            err("display profile does not support Absolute Colorimetric intent")

        cms_transform = ImageCms.buildProofTransform(
            inputProfile=image_profile,
            outputProfile=display_profile,
            proofProfile=simulated_profile,
            inMode=input_image.mode,
            outMode="RGB",
            renderingIntent=ImageCms.Intent.ABSOLUTE_COLORIMETRIC,
            proofRenderingIntent=opts.get_rendering_intent(),
            flags=(
                (ImageCms.Flags.SOFTPROOFING)
                | (0 if opts.no_bpc else ImageCms.Flags.BLACKPOINTCOMPENSATION)
                | (0 if opts.no_gamut_check else ImageCms.Flags.GAMUTCHECK)
            ),
        )

        print("processing color transform...")

        output_image = cms_transform.point(input_image)
        output_image.save(opts.output_filename)
        print("soft proof generated: %s" % opts.output_filename)

        # de requested ?
        if opts.de_filename is not None:
            print("calculating deltaE...")
            # convert input image to Lab if required
            if input_image.mode == "LAB":
                input_image_Lab = input_image

            else:
                input_image_Lab = ImageCms.applyTransform(
                    input_image,
                    ImageCms.buildTransform(
                        image_profile, lab_profile, input_image.mode, "LAB"
                    ),
                )

            # convert output image to Lab
            output_image_Lab = ImageCms.applyTransform(
                output_image,
                ImageCms.buildTransform(
                    ImageCms.ImageCmsProfile(
                        io.BytesIO(output_image.info["icc_profile"])
                    ),
                    lab_profile,
                    output_image.mode,
                    "LAB",
                ),
            )
            # calculate and create color difference (delta e) image
            de_image = create_de_image(
                opts.get_color_difference_formula(), input_image_Lab, output_image_Lab
            )
            # save color difference (delta e) image
            # create_de_image creates an RGB image, embed an sRGB profile
            # set keep_rgb so when saving JPG, it is not saved as YCbCr
            de_image.save(
                opts.de_filename,
                keep_rgb=True,
                icc_profile=ImageCms.ImageCmsProfile(
                    ImageCms.createProfile("sRGB")
                ).tobytes(),
            )
            print("deltaE output generated: %s" % opts.de_filename)


def run():
    opts = CommandOptions()
    parser = argparse.ArgumentParser(prog="benekli")
    parser.add_argument(
        "-d",
        "--display-profile",
        metavar="FILENAME",
        help="display (output) profile, default is active display",
    )
    parser.add_argument(
        "-e",
        "--de-formula",
        choices=["cie76", "cie94", "ciede2000"],
        help="delta E formula (default: %s)" % opts.de_formula,
        default=opts.de_formula,
    )
    parser.add_argument(
        "-i",
        "--input-image",
        metavar="FILENAME",
        help="input image filename",
        required=True,
    )
    parser.add_argument(
        "--input-profile",
        metavar="FILENAME",
        help="input profile to use (overrides embedded profile in input image)",
    )
    parser.add_argument(
        "--no-bpc",
        help="disable black point compensation (default: false)",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--no-gamut-check",
        help="disable gamut check (default: false)",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "-o", "--output-image", metavar="FILENAME", help="output image", required=True
    )
    parser.add_argument(
        "-q", "--output-de", metavar="FILENAME", help="output delta E image"
    )
    parser.add_argument(
        "-r",
        "--rendering-intent",
        choices=["p", "r", "s", "a"],
        help="rendering intent, p(erceptual), r(elative) colorimetric, s(aturation) or a(bsolute) colorimetric (default: %s)"
        % opts.rendering_intent,
        default=opts.rendering_intent,
    )
    parser.add_argument(
        "-s",
        "--simulated-profile",
        metavar="FILENAME",
        help="simulated (printer/paper) profile",
        required=True,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="enable verbose mode, use -vv to enable debug mode",
        action="count",
        default=0,
    )

    args = parser.parse_args()

    logging_format = "%(levelname)5s:%(filename)15s: %(message)s"

    logging.basicConfig(
        filename=log_file if False else None,
        level=logging.WARNING,
        format=logging_format,
    )

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
