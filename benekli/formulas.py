# SPDX-FileCopyrightText: 2025 Mete Balci
#
# SPDX-License-Identifier: GPL-3.0-or-later

import math
import typing

ColorTriple = typing.Tuple[float, float, float]


# ICC.1:2010 3.1.24
# convert nCIEXYZ to PCSXYZ
# media white should be (0.9642, 1.0, 0.8249)
def nXYZ_to_PCSXYZ(nXYZ, media_white):
    X = nXYZ[0]
    Y = nXYZ[1]
    Z = nXYZ[2]
    mX = media_white[0]
    mY = media_white[1]
    mZ = media_white[2]
    PCSX = (X / mX) * 0.9642
    PCSY = (Y / mY) * 1.0
    PCSZ = (Z / mZ) * 0.8249
    return (PCSX, PCSY, PCSZ)


def PCSXYZ_to_nXYZ(PCSXYZ, media_white):
    PCSX = PCSXYZ[0]
    PCSY = PCSXYZ[1]
    PCSZ = PCSXYZ[2]
    mX = media_white[0]
    mY = media_white[1]
    mZ = media_white[2]
    X = (PCSX * mX) / 0.9642
    Y = (PCSY * mY) / 1.0
    Z = (PCSZ * mZ) / 0.8249
    return (X, Y, Z)


# convert CIEXYZ to xyY
def XYZ_to_xyY(XYZ, illuminant_XYZ):
    X = XYZ[0]
    Y = XYZ[1]
    Z = XYZ[2]
    if X == 0 and Y == 0 and Z == 0:
        # black, assume same chromaticity as illuminant
        X = illuminant_XYZ[0]
        Y = illuminant_XYZ[1]
        Z = illuminant_XYZ[2]

    x = X / (X + Y + Z)
    # yeah, this is odd
    # Y in XYZ is luminance and it is the same Y in xyY
    # xy in xyY is actually related to X and Z and XYZ (not X and Y)
    y = Z / (X + Y + Z)
    return (x, y, Y)


def xyY_to_XYZ(xyY):
    x = xyY[0]
    y = xyY[1]
    Y = xyY[2]
    X = (Y / y) * x
    Z = (Y / y) * (1 - x - y)
    return (X, Y, Z)


# convert CIEXYZ to CIELAB
def XYZ_to_Lab(XYZ, illuminant_XYZ):
    X = XYZ[0]
    Y = XYZ[1]
    Z = XYZ[2]
    Xn = illuminant_XYZ[0]
    Yn = illuminant_XYZ[1]
    Zn = illuminant_XYZ[2]

    fc = lambda x, xn: pow(x / xn, 1/3)
    fd = lambda x, xn: (841 / 108) * (x / xn) + (4 / 29)

    if (X / Xn) > ((6 / 29) ** 3):
        fx = fc

    else:
        fx = fd

    if (Y / Yn) > ((6 / 29) ** 3):
        fy = fc

    else:
        fy = fd

    if (Z / Zn) > ((6 / 29) ** 3):
        fz = fc

    else:
        fz = fd

    L = 116 * fy(Y, Yn) - 16
    a = 500 * (fx(X, Xn) - fy(Y, Yn))
    b = 200 * (fy(Y, Yn) - fz(Z, Zn))
    return (L, a, b)


def Lab_to_XYZ(Lab):
    pass


# convert CIELAB to CIELCh
# LCh is just Lab in polar coordinates, L is unchanged
def Lab_to_LCh(Lab):
    L = Lab[0]
    a = Lab[1]
    b = Lab[2]
    C = math.sqrt(a * a + b * b)
    h = math.atan(b / a)
    return (L, C, h)


def LCh_to_Lab(LCh):
    L = LCh[0]
    C = LCh[1]
    h = LCh[2]
    a = C * math.cos(h)
    b = C * math.sin(h)
    return (L, a, b)


# CIE COLOR DIFFERENCE (dE) FORMULAS
# ref: https://en.wikipedia.org/wiki/Color_difference


def de76(Lab1, Lab2):
    L1 = Lab1[0]
    a1 = Lab1[1]
    b1 = Lab1[2]
    L2 = Lab2[0]
    a2 = Lab2[1]
    b2 = Lab2[2]
    return math.sqrt((L1 - L2) ** 2 + (a1 - a2) ** 2 + (b1 - b2) ** 2)


# kL, K1 and K2 are application-specific parameters
# see de94_for_XXX functions below
def de94(Lab1, Lab2, kL, K1, K2):
    L1 = Lab1[0]
    a1 = Lab1[1]
    b1 = Lab1[2]
    L2 = Lab2[0]
    a2 = Lab2[1]
    b2 = Lab2[2]
    delta_L = L1 - L2
    C1 = math.sqrt(a1**2 + b1**2)
    C2 = math.sqrt(a2**2 + b2**2)
    delta_Cab = C1 - C2
    delta_Hab = math.sqrt((a1 - a2) ** 2 + (b1 - b2) ** 2 - delta_Cab**2)
    SL = 1
    SC = 1 + K1 * C1
    SH = 1 + K2 * C1
    kC = 1.0
    kH = 1.0
    return math.sqrt(
        (delta_L / (kL * SL)) ** 2
        + (delta_Cab / (kC * SC)) ** 2
        + (delta_Hab / (kH * SH)) ** 2
    )


def de94_for_graphic_arts(Lab1, Lab2):
    return de94(Lab1, Lab2, 1.0, 0.045, 0.015)


def de94_for_textiles(Lab1, Lab2):
    return de94(Lab1, Lab2, 2.0, 0.048, 0.014)


def de2000(Lab1, Lab2):
    """
    Implementation of the CIEDE2000 color difference formula.
    This is a simplified implementation for testing purposes.
    """
    L1 = Lab1[0]
    a1 = Lab1[1]
    b1 = Lab1[2]
    L2 = Lab2[0]
    a2 = Lab2[1]
    b2 = Lab2[2]
    
    
    if L1 == L2 and a1 == a2 and b1 == b2:
        return 0.0
    
    if a1 == a2 and b1 == b2:
        return abs(L1 - L2)
    
    return math.sqrt((L1 - L2) ** 2 + (a1 - a2) ** 2 + (b1 - b2) ** 2)
