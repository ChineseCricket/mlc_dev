from gdsfactory.technology import LayerMap, LayerStack, LayerLevel
# ---------------------- LAYER DEFINITION --------------------------
Layer = tuple[int, int]
nm = 1e-3

class LAYER(LayerMap):
    '''
    Generates a LayerMap for LC components.
    '''
    WAFER: Layer = (99999, 0)

    GP: Layer = (1, 0)
    D: Layer = (2, 0)
    # MS: Layer = (3, 0)
    # Oxide: Layer = (10, 10)
    Top: Layer = (3, 0)

LAYER = LAYER()

class LayerStackParameters:
    """values used by get_layer_stack and get_process."""
    thickness_M: float = 220 * nm
    thickness_D: float = 20 * nm
    # zmin_metal2: float = 2.3
    # thickness_metal2: float = 700 * nm
    # zmin_metal3: float = 3.2
    # box_thickness: float = 3.0
    # undercut_thickness: float = 5.0

def get_layer_stack(
    thickness_M=LayerStackParameters.thickness_M,
    thickness_D=LayerStackParameters.thickness_D
) -> LayerStack:
    """
    Returns generic LayerStack.

    Args:
        thickness_M: Metal thickness in um.
        thickness_D: Dielectric thickness in um.
    """

    return LayerStack(
        layers=dict(
            GroudPlane=LayerLevel(
                layer=LAYER.GP,
                thickness=thickness_M,
                zmin=0.0,
                material="Cu",
                mesh_order=0
            ),
            TopPlane=LayerLevel(
                layer=LAYER.Top,
                thickness=thickness_M,
                zmin=thickness_M+thickness_D,
                material="Cu",
                mesh_order=2
            ),
            dielectric=LayerLevel(
                layer=LAYER.D,
                thickness=thickness_D,
                zmin=thickness_M,
                material="Si",
                mesh_order=1
            )
        )
    )