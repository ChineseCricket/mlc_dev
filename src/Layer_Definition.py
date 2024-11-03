from gdsfactory.technology import LayerMap, LayerStack, LayerLevel

 # ---------------------- LAYER DEFINITION --------------------------
Layer = tuple[int, int]
nm = 1e-3

class LAYER(LayerMap):
    '''
    Generates a LayerMap for LC components.
    '''
    WAFER: Layer = (999, 0)
    Frame: Layer = (99, 0)

    GP: Layer = (1, 0)
    TP: Layer = (2, 0)
    D: Layer = (15, 0)
    E0: Layer = (11, 0)
    E1: Layer = (12, 0)
    E2: Layer = (13, 0)
    Bond0: Layer = (20, 0)
    Bond1: Layer = (21, 0)
    Bond2: Layer = (22, 0)
    Bond3: Layer = (23, 0)

LAYER = LAYER()

class LayerStackParameters:
    """values used by get_layer_stack and get_process."""
    thickness_M: float = 220 * nm
    thickness_D: float = 25 * nm
    thickness_D2: float = 250 * nm
    thickness_M2: float = 520 * nm
    # zmin_metal2: float = 2.3
    # thickness_metal2: float = 700 * nm
    # zmin_metal3: float = 3.2
    # box_thickness: float = 3.0
    # undercut_thickness: float = 5.0

def get_layer_stack(
    thickness_M=LayerStackParameters.thickness_M,
    thickness_D=LayerStackParameters.thickness_D,
    thickness_D2=LayerStackParameters.thickness_D2,
    thickness_M2=LayerStackParameters.thickness_M2
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
                material="Nb",
                mesh_order=0
            ),
            TopPlane=LayerLevel(
                layer=LAYER.TP,
                thickness=thickness_M,
                zmin=thickness_M+thickness_D,
                material="Nb",
                mesh_order=0
            ),
            Etched0=LayerLevel(
                layer=LAYER.E0,
                thickness=thickness_D2,
                zmin=0,
                material="SiO2",
                mesh_order=0
            ),
            Etched1=LayerLevel(
                layer=LAYER.E1,
                thickness=thickness_D2,
                zmin=thickness_M,
                material="SiO2",
                mesh_order=0
            ),
            Etched2=LayerLevel(
                layer=LAYER.E2,
                thickness=thickness_D2,
                zmin=thickness_M+thickness_D+thickness_M,
                material="SiO2",
                mesh_order=0
            ),
            Bond0=LayerLevel(
                layer=LAYER.Bond0,
                thickness=thickness_M,
                zmin=thickness_M,
                material="Nb",
                mesh_order=0
            ),
            Bond1=LayerLevel(
                layer=LAYER.Bond1,
                thickness=thickness_M2,
                zmin=thickness_D2,
                material="Nb",
                mesh_order=0
            ),
            Bond2=LayerLevel(
                layer=LAYER.Bond2,
                thickness=thickness_M2,
                zmin=thickness_M+thickness_D2,
                material="Nb",
                mesh_order=0
            ),
            Bond3=LayerLevel(
                layer=LAYER.Bond3,
                thickness=thickness_M2,
                zmin=thickness_M+thickness_D+thickness_M,
                material="Nb",
                mesh_order=0
            ),
            Dielectric=LayerLevel(
                layer=LAYER.D,
                thickness=thickness_D,
                zmin=thickness_M,
                material="Si",
                mesh_order=0
            )
        )
    )

