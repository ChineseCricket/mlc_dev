#%%
'''
Code for Testing.
'''
import gdsfactory as gf
from Parameters_Classes import *
from Layer_Definition import *
from Component_Generator import *
from Chip_Generator import *
# ---------------------- INITIAILIZATION --------------------------
print("Note: default length unit is microns. \n")
sim = False # True if want to simulate the circuit
LAYER
# %%
Chip = newChip(4,'../logo/tsinghua logo large.gds',layer_order=[LAYER.GP, LAYER.TP,LAYER.E0,LAYER.D,LAYER.Bond0],ArrayFunctions={'default_array':newArray,'test_array':TestArray},test_array = {'via_pad_width':via_pad_width,'Ctype':'PPC','num_layers':3,'num_column':5,'num_row':8,'refix':[0,460,0,0]},default_array = {'via_pad_width':via_pad_width,'Ctype':'PPC','num_layers':3,'num_column':5,'num_row':8,'Frequencies': 
[[4200000., 3900000., 4600000., 4400000., 4800000.],
 [3700000., 1800000., 3200000., 1000000., 5000000.],
 [3000000., 1900000., 2600000., 1200000., 1300000.],
 [2200000., 3400000., 2100000., 2900000., 1600000.],
 [3600000., 1700000., 2300000., 1400000., 4100000.],
 [2800000., 2500000., 2000000., 2700000., 1500000.],
 [3800000., 3100000., 3300000., 4700000., 2400000.],
 [4000000., 4300000., 3500000., 4900000., 4500000.]],
'ratio_division':None})
Chip
Chip.write_gds("../output/STDChip.gds")
# %%
Chip = newChip(4,'../logo/tsinghua logo large.gds',layer_order=[LAYER.GP, LAYER.TP,LAYER.E0,LAYER.D,LAYER.Bond0],distribution=[(1,1,90,'test_array'),(2,1,90,'default_array'),(2,2,90,'default_array'),(3,1,0,'test_array'),(3,2,0,'default_array'),(3,3,0,'default_array'),(3,4,0,'default_array'),(3,5,0,'default_array'),(3,6,0,'test_array'),(4,1,90,'default_array'),(4,2,90,'default_array'),(5,1,90,'test_array')],inverse=True,InverseArrayPaths={'default_array':'../output/Array_without_voltage_division_inverse_er11.gds','test_array':'../output/TestArray_Inverse.gds'},ArrayFunctions={'default_array':newArray,'test_array':TestArray},test_array = {'via_pad_width':via_pad_width,'Ctype':'PPC','num_layers':3,'num_column':5,'num_row':8,'refix':[0,460,0,0]},default_array = {'via_pad_width':via_pad_width,'Ctype':'PPC','num_layers':3,'num_column':5,'num_row':8,'Frequencies': 
[[4200000., 3900000., 4600000., 4400000., 4800000.],
 [3700000., 1800000., 3200000., 1000000., 5000000.],
 [3000000., 1900000., 2600000., 1200000., 1300000.],
 [2200000., 3400000., 2100000., 2900000., 1600000.],
 [3600000., 1700000., 2300000., 1400000., 4100000.],
 [2800000., 2500000., 2000000., 2700000., 1500000.],
 [3800000., 3100000., 3300000., 4700000., 2400000.],
 [4000000., 4300000., 3500000., 4900000., 4500000.]],
'ratio_division':None})
Chip
Chip.write_gds("../output/12_Chip_inv.gds")
# %%
Chip = newChip(4,'../logo/tsinghua logo large.gds',layer_order=[LAYER.GP, LAYER.TP,LAYER.E0,LAYER.D,LAYER.Bond0],distribution=[(1,1,90,'test_array'),(2,1,90,'default_array'),(2,2,90,'default_array'),(3,1,0,'test_array'),(3,2,0,'default_array'),(2.5,3,0,'default_array'),(3,4,0,'default_array'),(3,5,0,'default_array'),(3,6,0,'test_array'),(4,1,90,'default_array'),(4,2,90,'default_array'),(5,1,90,'test_array')],ArrayFunctions={'default_array':newArray,'test_array':TestArray},test_array = {'via_pad_width':via_pad_width,'Ctype':'PPC','num_layers':3,'num_column':5,'num_row':8,'refix':[0,460,0,0]},default_array = {'via_pad_width':via_pad_width,'Ctype':'PPC','num_layers':3,'num_column':5,'num_row':8,'Frequencies': 
[[4200000., 3900000., 4600000., 4400000., 4800000.],
 [3700000., 1800000., 3200000., 1000000., 5000000.],
 [3000000., 1900000., 2600000., 1200000., 1300000.],
 [2200000., 3400000., 2100000., 2900000., 1600000.],
 [3600000., 1700000., 2300000., 1400000., 4100000.],
 [2800000., 2500000., 2000000., 2700000., 1500000.],
 [3800000., 3100000., 3300000., 4700000., 2400000.],
 [4000000., 4300000., 3500000., 4900000., 4500000.]],
'ratio_division':None})
Chip
# Chip.write_gds("../output/12_Chip.gds")
# %%'
# new 12chip
'''
下一版：在TestArray中放置一个可用万用表直接测量线阻的电路。
'''
Chip = newChip(4,'../logo/tsinghua logo large.gds',layer_order=[LAYER.GP, LAYER.TP,LAYER.E0,LAYER.D,LAYER.Bond0],distribution=[(1,1,90,'test_array'),(2,1,90,'default_array',0,0),(2,2,90,'default_array'),(3,1,0,'verify_array3',0,0.45),(3,1,90,'verify_array',0,0),(3,1,90,'verify_array2',0,0.22),(3,2,0,'default_array'),(3,3,0,'verify_array3',0,0.45),(3,3,90,'verify_array',0,0),(3,3,90,'verify_array2',0,0.22),(3,4,0,'default_array'),(3,5,0,'verify_array3',0,0.45),(3,5,90,'verify_array',0,0),(3,5,90,'verify_array2',0,0.22),(3,6,0,'default_array'),(4,1,90,'test_array'),(4,2,90,'test_array',0,0),(5,1,90,'default_array')],ArrayFunctions={'default_array':newArray,'test_array':TestArray,'verify_array':growArray,'verify_array2':growArray,'verify_array3':growArray},test_array = {'via_pad_width':via_pad_width,'Ctype':'PPC','num_layers':3,'num_column':5,'num_row':8,'refix':[0,460,0,0]},default_array = {'via_pad_width':via_pad_width,'Ctype':'PPC','num_layers':3,'num_column':5,'num_row':8,'Frequencies': 
[[4200000., 3900000., 4600000., 4400000., 4800000.],
 [3700000., 1800000., 3200000., 1000000., 5000000.],
 [3000000., 1900000., 2600000., 1200000., 1300000.],
 [2200000., 3400000., 2100000., 2900000., 1600000.],
 [3600000., 1700000., 2300000., 1400000., 4100000.],
 [2800000., 2500000., 2000000., 2700000., 1500000.],
 [3800000., 3100000., 3300000., 4700000., 2400000.],
 [4000000., 4300000., 3500000., 4900000., 4500000.]],
'ratio_division':None}, verify_array = {'via_pad_width':via_pad_width,'Ctype':'PPC','num_layers':3,'num_column':2,'num_row':2,'Frequencies':[[800000,700000],[600000,900000]],'ratio_division':None}, verify_array2 = {'via_pad_width':via_pad_width,'Ctype':'PPC','num_layers':3,'num_column':2,'num_row':2,'Frequencies':[[1000000,4000000],[3000000,2000000]],'ratio_division':None},verify_array3 = {'via_pad_width':via_pad_width,'Ctype':'PPC','num_layers':3,'num_column':4,'num_row':4,'Frequencies':[[2200000,1800000,2000000,2400000],[1000000,1200000,1600000,1400000],[1700000,1500000,1900000,1100000],[2500000,2300000,2100000,1300000]],'ratio_division':None,'cell_height':4000,'cell_width':2000})
Chip
# Chip.write_gds("../output/12_Chip_v.gds")
# %%
# new 12chip_inv
Chip = newChip(4,'../logo/tsinghua logo large.gds',layer_order=[LAYER.GP, LAYER.TP,LAYER.E0,LAYER.D,LAYER.Bond0],distribution=[(1,1,90,'test_array'),(2,1,90,'default_array',0,0),(2,2,90,'default_array'),(3,1,0,'verify_array3',0,0.45),(3,1,90,'verify_array',0,0),(3,1,90,'verify_array2',0,0.22),(3,2,0,'default_array'),(3,3,0,'verify_array3',0,0.45),(3,3,90,'verify_array',0,0),(3,3,90,'verify_array2',0,0.22),(3,4,0,'default_array'),(3,5,0,'verify_array3',0,0.45),(3,5,90,'verify_array',0,0),(3,5,90,'verify_array2',0,0.22),(3,6,0,'default_array'),(4,1,90,'test_array'),(4,2,90,'test_array',0,0),(5,1,90,'default_array')],ArrayFunctions={'default_array':newArray,'test_array':TestArray,'verify_array':growArray,'verify_array2':growArray,'verify_array3':growArray},inverse=True, InverseArrayPaths={'test_array':'../output/TestArray_Inverse.gds','default_array':'../output/Array_without_voltage_division_inverse_er11.gds','verify_array':'../output/verify_array.gds','verify_array2':'../output/verify_array2.gds','verify_array3':'../output/verify_array3.gds'}, test_array = {'via_pad_width':via_pad_width,'Ctype':'PPC','num_layers':3,'num_column':5,'num_row':8,'refix':[0,460,0,0]},default_array = {'via_pad_width':via_pad_width,'Ctype':'PPC','num_layers':3,'num_column':5,'num_row':8,'Frequencies': 
[[4200000., 3900000., 4600000., 4400000., 4800000.],
 [3700000., 1800000., 3200000., 1000000., 5000000.],
 [3000000., 1900000., 2600000., 1200000., 1300000.],
 [2200000., 3400000., 2100000., 2900000., 1600000.],
 [3600000., 1700000., 2300000., 1400000., 4100000.],
 [2800000., 2500000., 2000000., 2700000., 1500000.],
 [3800000., 3100000., 3300000., 4700000., 2400000.],
 [4000000., 4300000., 3500000., 4900000., 4500000.]],
'ratio_division':None}, verify_array = {'via_pad_width':via_pad_width,'Ctype':'PPC','num_layers':3,'num_column':2,'num_row':2,'Frequencies':[[800000,700000],[600000,900000]],'ratio_division':None}, verify_array2 = {'via_pad_width':via_pad_width,'Ctype':'PPC','num_layers':3,'num_column':2,'num_row':2,'Frequencies':[[1000000,4000000],[3000000,2000000]],'ratio_division':None},verify_array3 = {'via_pad_width':via_pad_width,'Ctype':'PPC','num_layers':3,'num_column':4,'num_row':4,'Frequencies':[[2200000,1800000,2000000,2400000],[1000000,1200000,1600000,1400000],[1700000,1500000,1900000,1100000],[2500000,2300000,2100000,1300000]],'ratio_division':None,'cell_height':4000,'cell_width':2000})
Chip.write_gds("../output/12_Chip_v_inv.gds")
Chip
# %%
TestChip = newChip(4,'../logo/tsinghua logo large.gds',layer_order=[LAYER.GP, LAYER.TP,LAYER.E0,LAYER.D,LAYER.Bond0],distribution=[(1,1,90,'test_array'),(2,1,90,'test_array'),(2,2,90,'test_array'),(3,1,0,'test_array'),(3,2,0,'test_array'),(3,3,0,'test_array'),(3,4,0,'test_array'),(3,5,0,'test_array'),(3,6,0,'test_array'),(4,1,90,'test_array'),(4,2,90,'test_array'),(5,1,90,'test_array')],inverse=True,InverseArrayPaths={'test_array':'../output/TestArray_Inverse.gds'},ArrayFunctions={'test_array':TestArray},test_array={'via_pad_width':via_pad_width,'Ctype' : 'PPC','num_layers' : 3,'num_column' : 5,'num_row' : 8,'refix' : [0,460,0,0]})
TestChip
TestChip.write_gds("../output/TestChip_inverse.gds")
# %%
TestChip = newChip(4,'../logo/tsinghua logo large.gds',layer_order=[LAYER.GP, LAYER.TP,LAYER.E0,LAYER.D,LAYER.Bond0],distribution=[(1,1,90,'test_array'),(2,1,90,'test_array'),(2,2,90,'test_array'),(3,1,0,'test_array'),(3,2,0,'test_array'),(3,3,0,'test_array'),(3,4,0,'test_array'),(3,5,0,'test_array'),(3,6,0,'test_array'),(4,1,90,'test_array'),(4,2,90,'test_array'),(5,1,90,'test_array')],ArrayFunctions={'test_array':TestArray},test_array={'via_pad_width':via_pad_width,'Ctype' : 'PPC','num_layers' : 3,'num_column' : 5,'num_row' : 8,'refix' : [0,460,0,0]})
TestChip
TestChip.write_gds("../output/TestChip.gds")
# %%
Array = TestArray(via_pad_width,'PPC',3,5,8,[0,460,0,0])
Array
Array.write_gds("../output/TestArray.gds")
# %%
RL = test_LineR_with_turn(LAYER.GP,4,10)
RL
# %%
try:
    gf.remove_from_cache(LCCircuit)
except:
    pass
if sim == False:
    LCCircuit = LCGenerator(via_pad_width,'PPC',3,2e6,None)
else:
    LCCircuit = LCGenerator_sim(via_pad_width,'PPC',3)
LCCircuit
#%%
TD = test_dielectric()
TD
TD.write_gds("../output/test_dielectric1.gds")
# %%
Array = newArray(via_pad_width,'PPC',3,5,8,[[4200000., 3900000., 4600000., 4400000., 4800000.],
 [3700000., 1800000., 3200000., 1000000., 5000000.],
 [3000000., 1900000., 2600000., 1200000., 1300000.],
 [2200000., 3400000., 2100000., 2900000., 1600000.],
 [3600000., 1700000., 2300000., 1400000., 4100000.],
 [2800000., 2500000., 2000000., 2700000., 1500000.],
 [3800000., 3100000., 3300000., 4700000., 2400000.],
 [4000000., 4300000., 3500000., 4900000., 4500000.]],None)
Array
# %%
Array = growArray(via_pad_width,'PPC',3,2,2,[[800000,700000],[600000,900000]],None)
Array
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
newarange = [[4200000., 3900000., 4600000., 4400000., 4800000.],
 [3700000., 1800000., 3200000., 1000000., 5000000.],
 [3000000., 1900000., 2600000., 1200000., 1300000.],
 [2200000., 3400000., 2100000., 2900000., 1600000.],
 [3600000., 1700000., 2300000., 1400000., 4100000.],
 [2800000., 2500000., 2000000., 2700000., 1500000.],
 [3800000., 3100000., 3300000., 4700000., 2400000.],
 [4000000., 4300000., 3500000., 4900000., 4500000.]]
# %%
'''
To generate 4 inch array with voltage division.
'''
import gdsfactory as gf
from Parameters_Classes import *
from Layer_Definition import *
from Component_Generator import *
from Chip_Generator import *
# ---------------------- INITIAILIZATION --------------------------
print("Note: default length unit is microns. \n")
sim = False # True if want to simulate the circuit
LAYER
Chip1 = newChip(4,'../logo/tsinghua logo large.gds',distribution=[(1,1,90),(2,1,90),(2,2,90),(3,1,0),(3,2,0),(3,3,0),(3,4,0),(3,5,0),(3,6,0),(4,1,90),(4,2,90),(5,1,90)],default_array = {'via_pad_width':via_pad_width,'Ctype':'PPC','num_layers':3,'num_column':5,'num_row':8,'Frequencies': 
[[4200000., 3900000., 4600000., 4400000., 4800000.],
 [3700000., 1800000., 3200000., 1000000., 5000000.],
 [3000000., 1900000., 2600000., 1200000., 1300000.],
 [2200000., 3400000., 2100000., 2900000., 1600000.],
 [3600000., 1700000., 2300000., 1400000., 4100000.],
 [2800000., 2500000., 2000000., 2700000., 1500000.],
 [3800000., 3100000., 3300000., 4700000., 2400000.],
 [4000000., 4300000., 3500000., 4900000., 4500000.]],
'ratio_division':[1,9]})
Chip1
Chip1.write_gds("../output/LC_array_4inch_with_votage_division_er11.gds")
# %%
'''
To generate 4 inch array without voltage division.
'''
import gdsfactory as gf
from Parameters_Classes import *
from Layer_Definition import *
from Component_Generator import *
from Chip_Generator import *
# ---------------------- INITIAILIZATION --------------------------
print("Note: default length unit is microns. \n")
sim = False # True if want to simulate the circuit
LAYER
Chip1 = newChip(4,'../logo/tsinghua logo large.gds',distribution=[(1,1,90),(2,1,90),(2,2,90),(3,1,0),(3,2,0),(3,3,0),(3,4,0),(3,5,0),(3,6,0),(4,1,90),(4,2,90),(5,1,90)],default_array = {'via_pad_width':via_pad_width,'Ctype':'PPC','num_layers':3,'num_column':5,'num_row':8,'Frequencies':
[[4200000., 3900000., 4600000., 4400000., 4800000.],
 [3700000., 1800000., 3200000., 1000000., 5000000.],
 [3000000., 1900000., 2600000., 1200000., 1300000.],
 [2200000., 3400000., 2100000., 2900000., 1600000.],
 [3600000., 1700000., 2300000., 1400000., 4100000.],
 [2800000., 2500000., 2000000., 2700000., 1500000.],
 [3800000., 3100000., 3300000., 4700000., 2400000.],
 [4000000., 4300000., 3500000., 4900000., 4500000.]],
'ratio_division':None})
Chip1
Chip1.write_gds("../output/LC_array_4inch_without_votage_division_er11.gds")
#%%
'''
To generate 4 inch array without voltage division and with inverse 1st layer.
'''
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
Chip2 = newChip(4,'../logo/tsinghua logo large.gds',distribution=[(1,1,90),(2,1,90),(2,2,90),(3,1,0),(3,2,0),(3,3,0),(3,4,0),(3,5,0),(3,6,0),(4,1,90),(4,2,90),(5,1,90)],default_array = {'via_pad_width':via_pad_width,'Ctype':'PPC','num_layers':3,'num_column':5,'num_row':8,'Frequencies':
[[4200000., 3900000., 4600000., 4400000., 4800000.],
 [3700000., 1800000., 3200000., 1000000., 5000000.],
 [3000000., 1900000., 2600000., 1200000., 1300000.],
 [2200000., 3400000., 2100000., 2900000., 1600000.],
 [3600000., 1700000., 2300000., 1400000., 4100000.],
 [2800000., 2500000., 2000000., 2700000., 1500000.],
 [3800000., 3100000., 3300000., 4700000., 2400000.],
 [4000000., 4300000., 3500000., 4900000., 4500000.]],
'ratio_division':None, 'fre_table_path':'../output/fre_table.txt'}, inverse=True, InverseArrayPaths={'default_array':'../output/Array_without_voltage_division_inverse_er11.gds'})

Chip2.write_gds("../output/LC_array_4inch_without_votage_division_inverseGP_er11.gds")
# %%
'''
To generate inverted first layer for 1 array.
'''
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
# Array = newArray(via_pad_width,'PPC',3,5,8,
# [[4200000., 3900000., 4600000., 4400000., 4800000.],
#  [3700000., 1800000., 3200000., 1000000., 5000000.],
#  [3000000., 1900000., 2600000., 1200000., 1300000.],
#  [2200000., 3400000., 2100000., 2900000., 1600000.],
#  [3600000., 1700000., 2300000., 1400000., 4100000.],
#  [2800000., 2500000., 2000000., 2700000., 1500000.],
#  [3800000., 3100000., 3300000., 4700000., 2400000.],
#  [4000000., 4300000., 3500000., 4900000., 4500000.]],
# ratio_division = None)
# Array = TestArray(via_pad_width,'PPC',3,5,8,[0,460,0,0])
# Array = growArray(via_pad_width,Ctype='PPC',num_layers=3,num_column=2,num_row=2,Frequencies=[[800000,700000],[600000,900000]],ratio_division=None)
# Array = growArray(via_pad_width,Ctype='PPC',num_layers=3,num_column=2,num_row=2,Frequencies=[[1000000,4000000],[3000000,2000000]],ratio_division=None)
Array = growArray(via_pad_width,Ctype='PPC',num_layers=3,num_column=4,num_row=4,Frequencies=[[2200000,1800000,2000000,2400000],[1000000,1200000,1600000,1400000],[1700000,1500000,1900000,1100000],[2500000,2300000,2100000,1300000]],ratio_division=None,cell_height=4000,cell_width=2000)
# Array
Test = gf.Component()
Array = Test << Array
Wafer = Test << gf.components.rectangle(size = (Array.xsize, Array.ysize), layer = (999,0))
Wafer.xmin = Array.xmin
Wafer.ymin = Array.ymin
Test
#%%
try:
  gf.remove_from_cache(S)
except:
   pass
S = gf.geometry.boolean(Test.extract([LAYER.WAFER]),Test.extract([LAYER.GP]),'A-B',layer = (1,0))
S
# %%
'''
To generate Logo pattern.
'''
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
1/(3e-6*(2*4e6*3.14)**2)
# %%
def TestFunc(Func,**kwargs):
    print(kwargs)
    for kwarg in kwargs:
        print(kwargs[kwarg])
        Func(**kwargs[kwarg])
    return 1

def Test(a=0,b=0,c=0,d=0):
    print(a,b,c,d)
    return a+b
# %%
TestFunc(Test,Test={'a': 1, 'b': 2})
# %%
dict2 = {'a': 1, 'b': 2}
for i, x in enumerate(dict2):
    print(i,x)


# %%
Test = gf.Component()
outline = Test << gf.geometry.boolean(gf.geometry.offset(gf.components.rectangle(size=(5000, 10000)), distance=75, use_union=True, layer=LAYER.GP),gf.components.rectangle(size=(5000, 10000)),'A-B')
outline2 = Test << gf.geometry.offset(gf.components.rectangle(size=(5000, 5000)), distance=75, use_union=False, layer=LAYER.GP)
# outline = Test << gf.geometry.outline(gf.components.rectangle(size=(5000, 10000)), distance=75, layer=LAYER.GP, join_first=False)
# outline2 = Test << gf.geometry.outline(gf.components.rectangle(size=(5000, 5000)), distance=75, layer=LAYER.GP)
Test
# %%
# %%