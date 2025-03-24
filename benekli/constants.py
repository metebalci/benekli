# SPDX-FileCopyrightText: 2025 Mete Balci
#
# SPDX-License-Identifier: GPL-3.0-or-later

# name => (cie 1931 2 deg: x, y) (cie 1964 10 deg: x, y) (cct)]
STANDARD_ILLUMINANTS_xy = {
    # A=incandescent/tungsten
    "A": [(0.44758, 0.40745), (0.45117, 0.40594), 2856],
    # D50=horizon light, ICC profile PCS
    "D50": [(0.34567, 0.35850), (0.34773, 0.35962), 5003],
    # D65=noon daylight, television/sRGB color space
    "D65": [(0.31272, 0.32903), (0.31382, 0.33100), 6504],
}

# ICC.1:2010 3.1.21 PCS illuminant
# CIE illuminant D50
PCS_illuminant_nXYZ = (0.9642, 1.0, 0.8249)
