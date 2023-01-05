"""
====================
Simple tool wrappers
====================

:Authors: - Florian Dupeyron <florian.dupeyron@mugcat.fr>
:Date: January 2023
"""

def ifp(x=""):
    """
    InterFace Prefix. Prefix an interface name with pyxnet- for easier identification.
    Call with no parameter to just return the prefix.
    """
    return f"pxn-{x}"


def sth(x):
    """
    ShorTHand. Generate a shorthand name on 3 characters.
    """
    return x
    #return f"{x[:2]}{x[-1]}" if len(x) > 3 else x


def ifs(x):
    """
    Return an interface name within the size of IFNAMSIZ=16 characters, including
    null terminating byte (so max 15 chars.).
    """

    return x[0:min(len(x), 16)]