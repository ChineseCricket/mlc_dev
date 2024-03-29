# %%
import gdsfactory as gf
from Parameters_Classes import *
from Layer_Definition import *
from Component_Generator import *
from Chip_Generator import *
# %%
# ---------------------- INITIAILIZATION --------------------------
print("Note: default length unit is microns. \n")
# Output location for gds file
directory = '../output/'
filename = 'Inductor.gds'
fileoutput = directory + filename
sim = False # True if want to simulate the circuit
LAYER
# %%
Chip = newCChip(4,via_pad_width,'PPC',3,5,8,
                  [[1e6, 2e6, 3.1e6, 4.1e6, 5e6],
                   [1.8e6, 4.2e6, 2.5e6, 1.7e6, 3.2e6],
                   [3.3e6, 2.2e6, 4.3e6, 2.9e6, 4.8e6],
                   [4.9e6, 3.9e6, 1.2e6, 1.9e6, 3.4e6],
                   [1.3e6, 2.1e6, 4.7e6, 3.5e6, 1.6e6],
                   [3.6e6, 4.4e6, 1.5e6, 2.3e6, 2.8e6],
                   [4.0e6, 2.7e6, 3.7e6, 1.4e6, 4.5e6],
                   [4.6e6, 2.4e6, 3.0e6, 2.6e6, 3.8e6]],
                   '../logo/LTD Sign.gds',)
# %%
Chip
# %%
Chip.write_gds("../output/C_array_4inch_new.gds")
# %%
Chip = newCChip(2,via_pad_width,'PPC',3,5,8,
                  [[1e6, 2e6, 3.1e6, 4.1e6, 5e6],
                   [1.8e6, 4.2e6, 2.5e6, 1.7e6, 3.2e6],
                   [3.3e6, 2.2e6, 4.3e6, 2.9e6, 4.8e6],
                   [4.9e6, 3.9e6, 1.2e6, 1.9e6, 3.4e6],
                   [1.3e6, 2.1e6, 4.7e6, 3.5e6, 1.6e6],
                   [3.6e6, 4.4e6, 1.5e6, 2.3e6, 2.8e6],
                   [4.0e6, 2.7e6, 3.7e6, 1.4e6, 4.5e6],
                   [4.6e6, 2.4e6, 3.0e6, 2.6e6, 3.8e6]],
                   '../logo/LTD Sign.gds',)
# %%
Chip
# %%
Chip.write_gds("../output/C_array_2inch.gds")
# %%
try:
    gf.remove_from_cache(LCCircuit)
except:
    pass
if sim == False:
    LCCircuit = LCGenerator(via_pad_width,'PPC',3)
else:
    LCCircuit = LCGenerator_sim(via_pad_width,'IDC',3)
# %%
LCCircuit
# %%
try:
    gf.remove_from_cache(LCCircuit)
except:
    pass

LCCircuit = LGenerator_sim(3)
# %%
LCCircuit
# %%
LCCircuit.write_gds("../output/C_array_2inch.gds")
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

# %%
8.5*8.85e-12/25e-9
# %%
1.4*4 #互感加强？
# %%
7 - 1.4*4 #相当于多了一个线圈???如果再多拆几份会怎样？
# %%
3/5
# %%
790/500 * 2000
# %%
def func(Frequency = 1e6):
    l_um = 6000
    h = 1   # [microns] thickness of substrate
    er = 8.5 # dielectric constant, using Silicon = 11.7
    W = 4
    Cap = 1/(L.inductance*(2*Frequency*numpy.pi)**2)# desired capacitance    Cap = 1/(L.inductance*(2*Frequency*numpy.pi)**2)# desired capacitance
    A1 = 4.409 * numpy.tanh( 0.55 * (h/W) ** (0.45)) * 1e-6 # (pF/um)
    A2 = 9.92 * numpy.tanh(0.52 * (h/W) ** (0.5)) * 1e-6   # (pF/um)

    C_picoF = Cap * 1e12 # go from farad to pico farad
    #C = (er + 1) * l * ( (N-3) * A1 + A2)
    # C / (  (er + 1) * l) = (N-3) * A1 + A2
    # ( C / ( (er + 1) * l ) - A2 ) / A1 = N -3
    # N = 3 + ( C / ( (er + 1) * l ) - A2 ) / A1
    
    N = int ( 3 + ( C_picoF / ( (er + 1) * l_um ) - A2 ) / A1 )
    return N
# %%
func()
# %%
350 * 40
# %%
4000 * 8
# %%
500 *40
# %%
import random
import math

class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0

def is_collision(rect1, rect2):
    return (rect1.x < rect2.x + rect2.width and
            rect1.x + rect1.width > rect2.x and
            rect1.y < rect2.y + rect2.height and
            rect1.y + rect1.height > rect2.y)

def is_inside_circle(rect, circle_radius):
    rect_center_x = rect.x + rect.width / 2
    rect_center_y = rect.y + rect.height / 2
    return math.sqrt(rect_center_x**2 + rect_center_y**2) < circle_radius

def place_rectangles(rectangles, circle_radius):
    for rect in rectangles:
        while True:
            rect.x = random.uniform(-circle_radius, circle_radius - rect.width)
            rect.y = random.uniform(-circle_radius, circle_radius - rect.height)
            if (all(not is_collision(rect, other_rect) for other_rect in rectangles if other_rect is not rect) and
                is_inside_circle(rect, circle_radius)):
                break

# Example usage:
rectangles = [Rectangle(1, 2), Rectangle(2, 3), Rectangle(1, 1)]
place_rectangles(rectangles, 10)
for rect in rectangles:
    print(f"Rectangle at ({rect.x}, {rect.y})")
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
a = [0,1,2,3]
a+=[3]
a
# %%
#column
#row
#rotation
#horizontal spacing
#vertical spacin
a,b = -(3,4)
a

# %%
