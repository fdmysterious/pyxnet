"""
===============
Diagram helpers
===============

:Authors: - Florian Dupeyron <florian.dupeyron@mugcat.fr>
:Date: January 2023
"""

import graphviz
from pathlib import Path

__assets_dir = (Path(__file__) / "..").resolve() / "assets"

def asset(x: Path):
    x = Path(x)
    return __assets_dir / x


def box_logo_node(dot, node_name, logo_path, text):
    """
    Generates a node with a box shape and some logo
    in it.
    """

    dot.node(node_name, label=f"""<
        <TABLE BORDER="0">
            <TR><TD WIDTH="64" HEIGHT="64" FIXEDSIZE="TRUE"><IMG SRC="{logo_path!s}" SCALE="BOTH"/></TD></TR>
            <TR><TD>{text}</TD></TR>
        </TABLE>>""", shape="box")