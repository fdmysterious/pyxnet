"""
===============
Diagram helpers
===============

:Authors: - Florian Dupeyron <florian.dupeyron@mugcat.fr>
:Date: January 2023
"""

import graphviz

def box_logo_node(dot, node_name, logo_path, text):
    """
    Generates a node with a box shape and some logo
    in it.
    """

    dot.node(node_name, label=f"""<
        <TABLE BORDER="0">
            <TR><TD WIDTH="64" HEIGHT="64" FIXEDSIZE="TRUE"><IMG SRC="{logo_path}" SCALE="BOTH"/></TD></TR>
            <TR><TD>{text}</TD></TR>
        </TABLE>>""", shape="box")