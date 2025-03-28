
This project is still a work-in-progress.

# benekli

benekli is a helper utility for soft proofing images. It has two purposes:

- generate soft proofs of the images/photos (i.e. how a photo would look like when it is printed)
- calculate color difference (delta E) between the original and soft proofs, so the best representation can be selected

Soft proofing can be done in many applications including Adobe Photoshop. However, it is cumbersome to use it with multiple images, with multiple simulated profiles and with different proofing options (e.g. rendering intent, black point compensation). This process can be automated with benekli.

The color difference (delta E) can be calculated with some applications or tools, but it is not that common in user applications (such as Photoshop or Lightroom). benekli can calculate delta E according to CIE 1976, CIE 1994 or CIEDE 2000 formulas and it generates an RGB image representing the delta E values. By using an heuristic, the best output (which printer/paper, which rendering intent, with or without black point compensation) can be found.

benekli is a Turkish word meaning spotted, speckled or mottled in English, i.e. "benekli elbise" means "spotty dress".

# Installation

benekli is a Python application using Pillow imaging library. It can be installed from pypi repository.

```
$ pip install benekli
```

The availability of the required Pillow modules: littlecms2, libtiff and jpg are checked in runtime.

# Usage

The repository contains [a scaled down version of Bill Atkinson's Fourteen Balls test image](FourteenBalls.tif)

To soft proof Fourteen Balls test image (which is an extreme example in ProPhoto RGB color space) simulating my printer (Epson SC-P800) using Epson Archival Matte paper (SC-P800...Matte.icc) on my display (BenQ SW271, display.icc):

```
$ benekli -v -s SC-P800\ Series\ Epson\ Archival\ Matte.icc -d display.icc -i FourteenBalls.tif -o FourteenBalls.p.bpc.tif -r p --bpc

 INFO:     benekli.py: input image is RGB
 INFO:     benekli.py: using the embedded profile in FourteenBalls.tif
 INFO:     benekli.py: image profile: ProPhoto RGB
 INFO:     benekli.py: simulated profile: SC-P800 Series Epson Archival Matte
 INFO:     benekli.py: display profile: SW271 1_D50_L100_G22_2025-03-18T14.58.41Z
soft proof generated: FourteenBalls.p.bpc.tif
```

generates FourteenBalls.p.bpc.tif soft proof image.

Be aware that what you will see below will be different depending on how wide the color gamut of your display is. I am checking these on a wide-gamut display with ~100% AdobeRGB coverage. You can test your display at [wide-gamut test page](https://www.wide-gamut.com/test).

Fourteen Balls:

![Fourteen Balls test image by Bill Atkinson](FourteenBalls.tif)

Fourteen Balls soft proof image using Perceptual rendering intent (-r p) with Black Point Compensation (--bpc):

![Fourteen Balls soft proof with perceptual rendering intent and black point compensation](FourteenBalls.p.bpc.tif)

# License

Copyright (C) 2025 Mete Balci

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.