
This project is still a work-in-progress.

# benekli

benekli is a helper utility for soft proofing images. It has two purposes:

- generate soft proofs of the images/photos (i.e. how a photo would look like when it is printed)
- calculate color difference (delta E) between the original and soft proofs, so the best representation can be selected

Soft proofing can be done in many applications including Adobe Photoshop. However, it is cumbersome to use it with multiple images, with multiple simulated profiles and with different proofing options (e.g. rendering intent, black point compensation). This process can be easily automated with benekli.

The color difference (delta E) can be calculated with some applications or tools, but it is not that common in user applications. benekli can calculate delta E according to CIE 1976, CIE 1994 or CIEDE 2000 formulas and it generates an RGB image representing the delta E values.

benekli is a Turkish word meaning spotted, speckled or mottled in English, i.e. benekli elbise means spotty dress.

# Installation

benekli is a Python application using Pillow imaging library. It can be installed from pip.

```
$ pip install benekli
```

Check the installation with:

```
$ benekli
```

# Usage

To be written.

# License

benekli
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