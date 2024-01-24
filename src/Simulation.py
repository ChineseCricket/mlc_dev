# %%
%load_ext autoreload
%autoreload 2
# %%
gt.material_name_to_medium
# %%
import gdsfactory as gf
from gdsfactory.cross_section import rib
from gdsfactory.generic_tech import LAYER, LAYER_STACK
from gdsfactory.technology import LayerStack

from gplugins.fdtdz.get_sparameters_fdtdz import get_sparameters_fdtdz

length = 10

c = gf.Component()
waveguide_rib = c << gf.components.straight(length=length, cross_section=rib)
nitride_feature = c << gf.components.circle(radius=2, layer=LAYER.WGN)
nitride_feature.x = 5
padding = c << gf.components.bbox(
    waveguide_rib.bbox, top=2, bottom=2, layer=LAYER.WAFER
)
c.add_ports(gf.components.straight(length=length).get_ports_list())

c.plot()
# %%
# define a mapping of pdk material names to tidy3d medium objects
mapping = {
    "si": td.Medium(name="Si", permittivity=3.47**2),
    "sio2": td.Medium(name="SiO2", permittivity=1.47**2),
}

# setup the tidy3d component
c = gt.Tidy3DComponent(
    component=component,
    layer_stack=LAYER_STACK,
    material_mapping=mapping,
    pad_xy_inner=2.0,
    pad_xy_outer=2.0,
    pad_z_inner=0,
    pad_z_outer=0,
    extend_ports=2.0,
)

# plot the component and the layerstack
fig = plt.figure(constrained_layout=True)
gs = fig.add_gridspec(ncols=2, nrows=3, width_ratios=(3, 1))
ax0 = fig.add_subplot(gs[0, 0])
ax1 = fig.add_subplot(gs[1, 0])
ax2 = fig.add_subplot(gs[2, 0])
axl = fig.add_subplot(gs[1, 1])
c.plot_slice(x="core", ax=ax0)
c.plot_slice(y="core", ax=ax1)
c.plot_slice(z="core", ax=ax2)
axl.legend(*ax0.get_legend_handles_labels(), loc="center")
axl.axis("off")
plt.show()
# %%
LAYER_STACK.layers.pop("substrate", None)

# setup the tidy3d component
c = gt.Tidy3DComponent(
    component=component,
    layer_stack=LAYER_STACK,
    material_mapping=mapping,
    pad_xy_inner=2.0,
    pad_xy_outer=2.0,
    pad_z_inner=0,
    pad_z_outer=0,
    extend_ports=2.0,
)

# plot the component and the layerstack
fig = plt.figure(constrained_layout=True)
gs = fig.add_gridspec(ncols=2, nrows=3, width_ratios=(3, 1))
ax0 = fig.add_subplot(gs[0, 0])
ax1 = fig.add_subplot(gs[1, 0])
ax2 = fig.add_subplot(gs[2, 0])
axl = fig.add_subplot(gs[1, 1])
c.plot_slice(x="core", ax=ax0)
c.plot_slice(y="core", ax=ax1)
c.plot_slice(z="core", ax=ax2)
axl.legend(*ax0.get_legend_handles_labels(), loc="center")
axl.axis("off")
plt.show()
# %%
c.plot_slice(x="core")
# %%
# initialize the tidy3d ComponentModeler
modeler = c.get_component_modeler(
    center_z="core", port_size_mult=(6, 4), sim_size_z=3.0
)

# we can plot the tidy3d simulation setup
fig, ax = plt.subplots(2, 1)
modeler.plot_sim(z=c.get_layer_center("core")[2], ax=ax[0])
modeler.plot_sim(x=c.ports[0].center[0], ax=ax[1])
fig.tight_layout()
plt.show()
# %%
c = gf.components.straight(length=2)
sp = gt.write_sparameters(
    c, filepath=PATH.sparameters_repo / "straight_3d.npz", sim_size_z=4
)
gp.plot.plot_sparameters(sp)
# %%
