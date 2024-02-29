# THIS SCRIPT CONTAINS THE CLASSES USED IN THE GENERATION OF THE RESONATOR CHIP
import numpy
class Chip:
    def __init__(self):
        #general information
        self.name = "CHIP NAME"
        self.date = "DATE"
        #geometry
        self.num_LC_rows = 5 #dummy value
        self.num_LC_cols = 5 #dummy value
        #frequency information
        self.frequency_schedule = numpy.zeros(self.num_LC_rows * self.num_LC_cols)
        self.channel_order = numpy.zeros(self.num_LC_rows * self.num_LC_cols)
        self.num_LCs = 0 #dummy value
        #WIRING PARAMETERS
        self.TL_width = 10 # width of transmission line
        self.wire2wire_space = 20 # space between wires
        self.wiring_gap = 500 # wiring gap for the corners of the chip
        self.LC2LC_y_gap = 180
        self.LC2LC_x_gap = 1000
        
class PadClass:
    def __init__(self):
        self.width0 = 500
        self.width1 = 100
        self.length1 = 350
        self.spacing = 20
        
        
class InductorClass:
# numLayers : number of etched layers    
    def __init__(self, numLayers):
        self.num_layers = numLayers # number of etched layers
        self.gap_width = 2 #microns 
        self.line_width = 2 # microns
        self.num_turns = 3#20 # number of turns in coil
        self.outer_diameter = 128#332#664 # size of inductor
        self.inductance = 3e-6 # inductance [Henry]
        
        if numLayers == 1:
            self.type = "with_pads"
            self.pad_gap = 20
            self.pad_width = 100
            self.pad_length = 248
            self.height = self.pad_width + self.pad_gap +  self.outer_diameter
        else:
            self.type = "without_pads"
            self.height = self.outer_diameter
        
class CapacitorClass:
    def __init__(self, Ctype, numLayers, Frequency):
    # numLayers : number of etched layers
        self.type = Ctype # save this information
        self.num_layers = numLayers
        if Ctype == "PPC":  # parallel plate capacitor
            #used in parallel plate capacitor -- maybe create this?
            self.length = CalculatePPCapacitorParameters(Frequency)
            self.height = self.length
        if Ctype == "IDC": #interdigital capacitor
            #used in interdigitated capacitor
            self.gap_width = 4
            self.line_width = 4
            self.base_height = 100 
            self.width = 100
            self.er = 8.5 # dielectric constant, using Silicon = 11.7
            self.h = 220e-3   # [microns] thickness of substrate
            self.finger_num, self.line_height = CalculateIDCapacitorParameters(Frequency, 1.35e-6, self.h, self.line_width, self.er)
            self.height = self.base_height * 2 + self.line_height + self.gap_width # total height of capacitor
            self.small_freq_offset =  0 #6150 - (3850) + 500
        
class ResonatorClass:
    def __init__(self, height, width):
        self.height = height 
        self.width = width
        self.gap = 50 # space between capacitor and inductor
        self.channel_text_size = 80
        self.channel_text_gap = 10
        self.total_height = height

class BoundaryClass:
    def __init__(self):
        self.gap = 100
        self.line_width = 50

def CalculatePPCapacitorParameters(Frequency):
    # calculate the length of the parallel plate capacitor based on the desired capacity.
    # C = epsilon * A / d
    # A = length * length
    # d = 25 nm
    # epsilon = 8.5*8.85e-12
    # C = 8.5*8.85e-12/25e-9 * length * length
    # length = sqrt(C / 0.003009)
    Capacity = 1/(3e-6*(2*Frequency*numpy.pi)**2)
    return numpy.sqrt(Capacity / 0.003009)*1e6 # convert to microns

def CalculateIDCapacitorParameters(Frequency, L_lumped, h, W, er):
    #Calculate capacitance
    Cap = 1/(3e-6*(2*Frequency*numpy.pi)**2)# desired capacitance
    #print("Capacitance = %.2E Farads" %(Cap))        
        
    #SELECT LINE WIDTH, HEIGHT AND GAP WIDTH BASED ON FREQUENCY
    f = 0
    line_height_list = [6600,4000,3600,3000,2000,1500,1000]
    finger_freq_range = [1.8e6,1e9,2e9,3e9,4e9,5e9,6e9,7e9]
    l_um = line_height_list[0]
    while Frequency > finger_freq_range[f]:
        if Frequency > finger_freq_range[len(finger_freq_range) -1]:
            print("\nError!!! Frequency is out of range!\n")
            break 
        l_um = line_height_list[f]
        f = f + 1
        
    # calculate N   
    A1 = 4.409 * numpy.tanh( 0.55 * (h/W) ** (0.45)) * 1e-6 # (pF/um)
    A2 = 9.92 * numpy.tanh(0.52 * (h/W) ** (0.5)) * 1e-6   # (pF/um)

    C_picoF = Cap * 1e12 # go from farad to pico farad
    #C = (er + 1) * l * ( (N-3) * A1 + A2)
    # C / (  (er + 1) * l) = (N-3) * A1 + A2
    # ( C / ( (er + 1) * l ) - A2 ) / A1 = N -3
    # N = 3 + ( C / ( (er + 1) * l ) - A2 ) / A1
    
    N = int ( 3 + ( C_picoF / ( (er + 1) * l_um ) - A2 ) / A1 )
        
    #print("N = %d , l = %.2E (um) " %(N, l_um))    
    return N, l_um # number of fingers, length of finger

# def CalculateCapacitanceFromFrequency( L, freq_array, nfreq):
    
#     if nfreq == 1:
#         desired_C = ( 1 / (2*numpy.pi * freq_array) ) ** 2 / L
#         return desired_C
    
#     else:
    
#         #nfreq = len(freq_array)
#         desired_C_array = numpy.zeros(nfreq)
    
#         for f in range(nfreq):
#             freq = freq_array[f]
#             desired_C_array[f] = ( 1 / (2*numpy.pi * freq) ) ** 2 / L
    
#     return desired_C_array