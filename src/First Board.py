newarange = [[4200000., 3900000., 4600000., 4400000., 4800000.],
 [3700000., 1800000., 3200000., 1000000., 5000000.],
 [3000000., 1900000., 2600000., 1200000., 1300000.],
 [2200000., 3400000., 2100000., 2900000., 1600000.],
 [3600000., 1700000., 2300000., 1400000., 4100000.],
 [2800000., 2500000., 2000000., 2700000., 1500000.],
 [3800000., 3100000., 3300000., 4700000., 2400000.],
 [4000000., 4300000., 3500000., 4900000., 4500000.]]
# %%
import gdsfactory as gf
from Parameters_Classes import *
from Layer_Definition import *
from Component_Generator import *
from Chip_Generator import *
# ---------------------- INITIAILIZATION --------------------------
print("Note: default length unit is microns. \n")
sim = False # True if want to simulate the circuit
LAYER
Chip1 = newChip(newArray,4,'../logo/tsinghua logo large.gds',[(1,1,90),(2,1,90),(2,2,90),(3,1,0),(3,2,0),(3,3,0),(3,4,0),(3,5,0),(3,6,0),(4,1,90),(4,2,90),(5,1,90)],via_pad_width=via_pad_width,Ctype = 'PPC',num_layers = 3,num_column = 5,num_row = 8,Frequencies = 
                  [[1e6, 2e6, 3.1e6, 4.1e6, 5e6],
                   [1.8e6, 4.2e6, 2.5e6, 1.7e6, 3.2e6],
                   [3.3e6, 2.2e6, 4.3e6, 2.9e6, 4.8e6],
                   [4.9e6, 3.9e6, 1.2e6, 1.9e6, 3.4e6],
                   [1.3e6, 2.1e6, 4.7e6, 3.5e6, 1.6e6],
                   [3.6e6, 4.4e6, 1.5e6, 2.3e6, 2.8e6],
                   [4.0e6, 2.7e6, 3.7e6, 1.4e6, 4.5e6],
                   [4.6e6, 2.4e6, 3.0e6, 2.6e6, 3.8e6]],
                   ratio_division = [1,9])
Chip1
# Chip1.write_gds("../output/LC_array_4inch_with_votage_division_er11.gds")
# %%
import gdsfactory as gf
from Parameters_Classes import *
from Layer_Definition import *
from Component_Generator import *
from Chip_Generator import *
# ---------------------- INITIAILIZATION --------------------------
print("Note: default length unit is microns. \n")
sim = False # True if want to simulate the circuit
LAYER
Chip1 = newChip(newArray,4,'../logo/tsinghua logo large.gds',[(1,1,90),(2,1,90),(2,2,90),(3,1,0),(3,2,0),(3,3,0),(3,4,0),(3,5,0),(3,6,0),(4,1,90),(4,2,90),(5,1,90)],via_pad_width=via_pad_width,Ctype = 'PPC',num_layers = 3,num_column = 5,num_row = 8,Frequencies = 
                  [[1e6, 2e6, 3.1e6, 4.1e6, 5e6],
                   [1.8e6, 4.2e6, 2.5e6, 1.7e6, 3.2e6],
                   [3.3e6, 2.2e6, 4.3e6, 2.9e6, 4.8e6],
                   [4.9e6, 3.9e6, 1.2e6, 1.9e6, 3.4e6],
                   [1.3e6, 2.1e6, 4.7e6, 3.5e6, 1.6e6],
                   [3.6e6, 4.4e6, 1.5e6, 2.3e6, 2.8e6],
                   [4.0e6, 2.7e6, 3.7e6, 1.4e6, 4.5e6],
                   [4.6e6, 2.4e6, 3.0e6, 2.6e6, 3.8e6]],
                   ratio_division = None)
Chip1
Chip1.write_gds("../output/LC_array_4inch_without_votage_division_er11.gds")
#%%
import gdsfactory as gf
from Parameters_Classes import *
from Layer_Definition import *
from Component_Generator import *
from Chip_Generator import *
# ---------------------- INITIAILIZATION --------------------------
print("Note: default length unit is microns. \n")
# Output location for gds file
directory = '../output/'
filename = 'Inductor.gds'
fileoutput = directory + filename
sim = False # True if want to simulate the circuit
LAYER
Chip2 = newChip(newArray,4,'../logo/tsinghua logo large.gds',[(1,1,90),(2,1,90),(2,2,90),(3,1,0),(3,2,0),(3,3,0),(3,4,0),(3,5,0),(3,6,0),(4,1,90),(4,2,90),(5,1,90)],via_pad_width=via_pad_width,Ctype = 'PPC',num_layers = 3,num_column = 5,num_row = 8,Frequencies = 
                  [[1e6, 2e6, 3.1e6, 4.1e6, 5e6],
                   [1.8e6, 4.2e6, 2.5e6, 1.7e6, 3.2e6],
                   [3.3e6, 2.2e6, 4.3e6, 2.9e6, 4.8e6],
                   [4.9e6, 3.9e6, 1.2e6, 1.9e6, 3.4e6],
                   [1.3e6, 2.1e6, 4.7e6, 3.5e6, 1.6e6],
                   [3.6e6, 4.4e6, 1.5e6, 2.3e6, 2.8e6],
                   [4.0e6, 2.7e6, 3.7e6, 1.4e6, 4.5e6],
                   [4.6e6, 2.4e6, 3.0e6, 2.6e6, 3.8e6]],
                   ratio_division = None, inverse=True, InverseArrayPath='../output/Array_without_voltage_division_inverse_er11.gds')

Chip2.write_gds("../output/LC_array_4inch_without_votage_division_inverseGP_er11.gds")
# %%
Array = newArray(via_pad_width,'PPC',3,5,8,
                  [[1e6, 2e6, 3.1e6, 4.1e6, 5e6],
                   [1.8e6, 4.2e6, 2.5e6, 1.7e6, 3.2e6],
                   [3.3e6, 2.2e6, 4.3e6, 2.9e6, 4.8e6],
                   [4.9e6, 3.9e6, 1.2e6, 1.9e6, 3.4e6],
                   [1.3e6, 2.1e6, 4.7e6, 3.5e6, 1.6e6],
                   [3.6e6, 4.4e6, 1.5e6, 2.3e6, 2.8e6],
                   [4.0e6, 2.7e6, 3.7e6, 1.4e6, 4.5e6],
                   [4.6e6, 2.4e6, 3.0e6, 2.6e6, 3.8e6]],
                   None)
# %%
Array
# %%
import gdsfactory as gf
from Parameters_Classes import *
from Layer_Definition import *
from Component_Generator import *
from Chip_Generator import *
# ---------------------- INITIAILIZATION --------------------------
print("Note: default length unit is microns. \n")
sim = True # True if want to simulate the circuit
LAYER
try:
    gf.remove_from_cache(LCCircuit)
except:
    pass
if sim == False:
    LCCircuit = LCGenerator(via_pad_width,'PPC',3,4e6,None)
else:
    LCCircuit = LCGenerator_sim(via_pad_width,'PPC',3)
# %%
LCCircuit
#%%
C = CGenerator(via_pad_width,'PPC',3,5e6,0.9)
# %%
C
(0.3169-0.3047)/0.3047
# %%
C.write_gds("../output/C.gds")
# %%
Chip = newChip(newCArray,4,'../logo/tsinghua logo large.gds',via_pad_width=via_pad_width,Ctype = 'PPC',num_layers = 3,num_column = 5,num_row = 8,Frequencies = 
                  [[1e6, 2e6, 3.1e6, 4.1e6, 5e6],
                   [1.8e6, 4.2e6, 2.5e6, 1.7e6, 3.2e6],
                   [3.3e6, 2.2e6, 4.3e6, 2.9e6, 4.8e6],
                   [4.9e6, 3.9e6, 1.2e6, 1.9e6, 3.4e6],
                   [1.3e6, 2.1e6, 4.7e6, 3.5e6, 1.6e6],
                   [3.6e6, 4.4e6, 1.5e6, 2.3e6, 2.8e6],
                   [4.0e6, 2.7e6, 3.7e6, 1.4e6, 4.5e6],
                   [4.6e6, 2.4e6, 3.0e6, 2.6e6, 3.8e6]]
                   )
# %%
Chip
# %%
Chip.write_gds("../output/C_array_4inch_new.gds")
# %%
Chip = newChip(newCArray,2,'../logo/LTD Sign.gds',via_pad_width=via_pad_width,Ctype = 'PPC',num_layers = 3,num_column = 5,num_row = 8,Frequencies = 
                  [[1e6, 2e6, 3.1e6, 4.1e6, 5e6],
                   [1.8e6, 4.2e6, 2.5e6, 1.7e6, 3.2e6],
                   [3.3e6, 2.2e6, 4.3e6, 2.9e6, 4.8e6],
                   [4.9e6, 3.9e6, 1.2e6, 1.9e6, 3.4e6],
                   [1.3e6, 2.1e6, 4.7e6, 3.5e6, 1.6e6],
                   [3.6e6, 4.4e6, 1.5e6, 2.3e6, 2.8e6],
                   [4.0e6, 2.7e6, 3.7e6, 1.4e6, 4.5e6],
                   [4.6e6, 2.4e6, 3.0e6, 2.6e6, 3.8e6]]
                   )
# %%
Chip
# %%
Chip.write_gds("../output/C_array_2inch.gds")
# %%
import gdsfactory as gf
from Parameters_Classes import *
from Layer_Definition import *
from Component_Generator import *
from Chip_Generator import *
# ---------------------- INITIAILIZATION --------------------------
print("Note: default length unit is microns. \n")
sim = True # True if want to simulate the circuit
LAYER
try:
    gf.remove_from_cache(LCCircuit)
except:
    pass

LCCircuit = SLGenerator_sim(3)
# %%
LCCircuit
# %%
LCCircuit.write_gds("../output/SInd_4u.gds")
# %%
LAYER_STACK = get_layer_stack()
layer_stack = LAYER_STACK
scene = LCCircuit.to_3d(layer_stack=layer_stack)
scene.show()
# %%
help(scene)
# %%
scene.export('../output/Inductor1.stl','stl')
# %%
# use klayout.lay and klayout.db for standalone module
import pya as klay
import pya as kdb

ly = kdb.Layout()
ly.dbu = 0.001

top_cell = ly.create_cell("TOP")

image = klay.Image("../logo/LTD Sign.png")

# threshold
thr = 128

# pixel dimension in DBU (EDIT: comment was misleading)
pixel_size = int(0.5 + 10 / ly.dbu)

image_geo = kdb.Region()

for y in range(0, image.height()):
  on = False
  xstart = 0
  for x in range(0, image.width()):
    # take green (component 1) value for "intensity"
    value = image.get_pixel(x, y, 1) <= thr
    if value != on:
      on = value
      if on: 
        xstart = x
      else:
        image_geo.insert(kdb.Box(xstart, y, x, y + 1) * pixel_size)
  # EDIT: added these two lines
  if on: 
    image_geo.insert(kdb.Box(xstart, y, image.width(), y + 1) * pixel_size)

image_geo = image_geo.merged()

layer = ly.layer(1, 0)
top_cell.shapes(layer).insert(image_geo)

# image_geo = image_geo.smoothed(pixel_size * 0.99)

# layer = ly.layer(2, 0)
# top_cell.shapes(layer).insert(image_geo)

ly.write("../logo/LTD Sign.gds")
# %%
import gdsfactory as gf
from Parameters_Classes import *
from Layer_Definition import *
from Component_Generator import *
from Chip_Generator import *
# ---------------------- INITIAILIZATION --------------------------
print("Note: default length unit is microns. \n")
# Output location for gds file
directory = '../output/'
filename = 'Inductor.gds'
fileoutput = directory + filename
sim = False # True if want to simulate the circuit
LAYER
# Chip1 = newChip(newArray,4,'../logo/tsinghua logo large.gds',[(1,1,90),(2,1,0),(2,2,0),(3,1,90)],via_pad_width=via_pad_width,Ctype = 'PPC',num_layers = 3,num_column = 5,num_row = 8,Frequencies =   [[1e6, 2e6, 3.1e6, 4.1e6, 5e6],
#                    [1.8e6, 4.2e6, 2.5e6, 1.7e6, 3.2e6],
#                    [3.3e6, 2.2e6, 4.3e6, 2.9e6, 4.8e6],
#                    [4.9e6, 3.9e6, 1.2e6, 1.9e6, 3.4e6],
#                    [1.3e6, 2.1e6, 4.7e6, 3.5e6, 1.6e6],
#                    [3.6e6, 4.4e6, 1.5e6, 2.3e6, 2.8e6],
#                    [4.0e6, 2.7e6, 3.7e6, 1.4e6, 4.5e6],
#                    [4.6e6, 2.4e6, 3.0e6, 2.6e6, 3.8e6]],
#                    ratio_division = [1,9],inverse=False)
# Chip1
# %%
gf.geometry.boolean(Chip1.extract([LAYER.WAFER]),Chip1.extract([LAYER.Bond0]),'A-B',layer = (1,0))
# %%
S = gf.geometry.boolean_polygons(Chip1.extract([LAYER.WAFER]),Chip1.extract([LAYER.Bond0]),'not',output_layer = (1,0))
# %%
S[1].show
# %%
Array = newArray(via_pad_width,'PPC',3,5,8,
                  [[1e6, 2e6, 3.1e6, 4.1e6, 5e6],
                   [1.8e6, 4.2e6, 2.5e6, 1.7e6, 3.2e6],
                   [3.3e6, 2.2e6, 4.3e6, 2.9e6, 4.8e6],
                   [4.9e6, 3.9e6, 1.2e6, 1.9e6, 3.4e6],
                   [1.3e6, 2.1e6, 4.7e6, 3.5e6, 1.6e6],
                   [3.6e6, 4.4e6, 1.5e6, 2.3e6, 2.8e6],
                   [4.0e6, 2.7e6, 3.7e6, 1.4e6, 4.5e6],
                   [4.6e6, 2.4e6, 3.0e6, 2.6e6, 3.8e6]],
                   None)
Array
# %%
Test = gf.Component()
Array = Test << Array
# %%
Wafer = Test << gf.components.rectangle(size = (Array.xsize, Array.ysize), layer = (999,0))
Wafer.xmin = Array.xmin
Wafer.ymin = Array.ymin
# %%
Test
# %%
S = gf.geometry.boolean(Test.extract([LAYER.WAFER]),Test,'not',layer = (1,0))
# %%
S
# %%
gf.remove_from_cache(S)
# %%
A = np.array([[1e6, 2e6, 3.1e6, 4.1e6, 5e6],
                   [1.8e6, 4.2e6, 2.5e6, 1.7e6, 3.2e6],
                   [3.3e6, 2.2e6, 4.3e6, 2.9e6, 4.8e6],
                   [4.9e6, 3.9e6, 1.2e6, 1.9e6, 3.4e6],
                   [1.3e6, 2.1e6, 4.7e6, 3.5e6, 1.6e6],
                   [3.6e6, 4.4e6, 1.5e6, 2.3e6, 2.8e6],
                   [4.0e6, 2.7e6, 3.7e6, 1.4e6, 4.5e6],
                   [4.6e6, 2.4e6, 3.0e6, 2.6e6, 3.8e6]]).flatten()
A.sort()
# %%
print(A)
# %%
32/123
# %%
import gdsfactory as gf
from Parameters_Classes import *
from Layer_Definition import *
from Component_Generator import *
from Chip_Generator import *
# ---------------------- INITIAILIZATION --------------------------
print("Note: default length unit is microns. \n")
sim = True # True if want to simulate the circuit
LAYER
try:
    gf.remove_from_cache(LCCircuit)
except:
    pass

LCCircuit = CGenerator(via_pad_width,'IDC',3,1e6,ratio = 1)
# %%
LCCircuit
# LCCircuit.write_gds("../output/PPC_5MHz.gds")
# %%
11.7*8.85e-12/25e-9
# %%
