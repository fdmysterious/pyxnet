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
    return f"pyxnet-{x}"