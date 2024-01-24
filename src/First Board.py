
# %%
import gdspy as gf

from Parameters_Classes import *
from Layer_Definition import *
from Component_Generator import *

# %%
# ---------------------- INITIAILIZATION --------------------------
print("Note: default length unit is microns. \n")
# Output location for gds file
directory = '../output/'
filename = 'test.gds'
fileoutput = directory + filename
sim = True # True if want to simulate the circuit
LAYER
# %%
try:
    gf.remove_from_cache(LCCircuit)
except:
    pass
if sim == False:
    LCCircuit = LCGenerator(via_pad_width,'PPC',3)
else:
    LCCircuit = LCGenerator_sim(via_pad_width,'PPC',3)

# %%
LCCircuit
# %%
LAYER_STACK = get_layer_stack()
layer_stack = LAYER_STACK
scene = LCCircuit.to_3d(layer_stack=layer_stack)
scene.show()
# %%
help(scene)
# %%
scene.export('../output/testboard.stl','stl')
# %%
