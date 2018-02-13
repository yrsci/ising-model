#!/usr/bin/python3

"""

Collection of functions required for ising-model.py and lattice_analysis.py. 3 sections:

1. Generating & updating lattice
- nearest_neighbours
- ham_calc
- update_lattice (nested function: p_flip)

2. Calculating lattice properties
- magnetisation
- energy

3. Visualising / analysing the lattice arrays
- pbm
- read_pbm
- gif_gen
- parse_input

"""


import numpy as np
import math
import imageio      # This module is used for the .gif generation


###
### 1. GENERATING & UPDATING LATTICE
###

def antiferro_lattice_gen(n):
    """
    Generates a 2D lattice of side length n populated with ordered
    1 and -1 elements, consistent with an antiferromagnetic lattice at
    T=0.
    """

    basic_lattice = np.ones((n,n), dtype=np.int)
    
    for i in range(0,n) :
        if i%2 == 0 :
            for j in range(0,n) :
                if j%2 == 0:
                    basic_lattice[i][j] = -1
            
        else :
            for j in range(0,n) :
                if j%2 != 0 :
                    basic_lattice[i][j] = -1

    return basic_lattice


def nearest_neighbours(lattice,i,j):

    """
    Identifies the nearest neighbours of a point (i,j) in a given lattice,
    implementing continuous border conditions. Returns an array of the values
    of those neighbours in the lattice (i.e. +1 or -1).
    """
    top = lattice[i-1,j]
    left = lattice[i,j-1]
    
    if i == lattice.shape[0]-1:
        bottom = lattice[0,j]
    else:
        bottom = lattice[i+1,j]
    
    if j == lattice.shape[1]-1:
        right = lattice[i,0]
    else:
        right = lattice[i,j+1]

    # Make an array of the neighbours
    neighbs = np.array([top,bottom,left,right])
    return neighbs


def ham_calc(particle,neighbours,h,magtype="ferro"):
    """
    Calculate the Hamiltonian for lattice element (i,j) based on nearest-neighbour 
    interaction, and interaction with an external field h (which may be zero). 
    Return the Hamiltonian value.
    """
    
    if magtype == "ferro" :
        J = 1
    elif magtype == "antiferro" :
        J = -1

    # Calculate the Hamiltonian for particle (i,j)
    ham_array = -J * particle * neighbours
    ham = 0.
    for val in range(0,len(ham_array)):
        ham += ham_array[val]

    # Add interaction with external field
    ham -= (h * particle)
   
    return (ham)


def update_lattice(lattice,T,h,magtype="ferro"):
    """
    Chooses a randomly-selected point in the lattice, calculates the probability the 
    spin will flip on each iteration, and updates the spin accordingly. Returns the 
    lattice with the updated spin. Can model either ferromagnetic or antiferromagnetic behaviour.
    """
    
    # Determine side length of lattice
    n = np.shape(lattice)[0]
    # Calculate number of sites in lattice
    N = n*n

    
    def p_flip(del_E):
        """
        Calculate the probability of a spin flip occurring for a given energy difference
        del_E using the Metropolis algorithm. Returns the flip probability.
        """
        
        # Define Boltzmann constant k
        k = 1.
        
        if del_E < 0.:
            p_flip = 1.0
        else:
            p_flip = ( math.e ** (-1 * del_E / (k * T) ) )

        return p_flip
    
    for num in range(0,N*2):
        # Randomly select integers i,j within lattice dimensions
        i = np.random.randint(0,n)
        j = np.random.randint(0,n)
            
        # Identify particle (i,j) and its nearest neighbours
        particle = lattice[i,j]    
        neighbours = nearest_neighbours(lattice,i,j)
        
        # Calculate the Hamiltonian of unflipped & flipped (i,j) using function ham_calc
        ham = ham_calc(particle,neighbours,h,magtype)
        ham_flip = ham_calc(-1*particle,neighbours,h,magtype)

        # Calculate the energy difference between spin states for particle (i,j)
        del_E = ham_flip - ham

        # Use the embedded function p_flip to calculate the spin flip probability for particle (i,j)
        probability = p_flip(del_E)
        
        # Apply the spin flip condition
        if probability == 1.0 or probability > np.random.rand():
            lattice[i,j] = -1 * lattice[i,j]
    
    return lattice



###
### 2. CALCULATING LATTICE PROPERTIES
###


def magnetisation(lattice):
    """
    Calculates net magnetisation M of a microstate by summing all values in the given 
    lattice. Returns a tuple of M and M**2 normalised by number of elements in the array.
    """
    
    # Determine side length of lattice
    n = np.shape(lattice)[0]
 
    # Initialise variable mag to act as running total for net magnetisation
    mag = 0.
    
    # Scan through each element in lattice and add its value to mag
    for i in lattice:
        for j in i:
            mag += j
    
    # Divide by total no. of lattice elements to calc net magnetisation per site
    mag_persite = mag / (n**2)
    # Square the value for calculating variance
    mag_persite_sq = mag_persite**2
    
    return mag_persite, mag_persite_sq



def energy(lattice,h,magtype="ferro"):
    """
    Calculates the net energy E of a microstate by summing the Hamiltonian for each 
    element (i,j) in the given lattice. Returns a tuple of E and E**2 normalised by 
    number of elements in the array
    """
    
    # Determine side length of lattice
    n = np.shape(lattice)[0]
    
    E = 0.
    
    for i in range(0,n):
        for j in range(0,n):
            neighbours = nearest_neighbours(lattice,i,j)
            E += ham_calc(lattice[i,j],neighbours,h,magtype)

    # Divide by 2 to correct for double-counting of spin pairs 
    E = E / 2.
    
    # Divide by total no. of lattice elements to calc net energy per site
    E_persite = E / (n**2)
    # Square the value for calculating variance
    E_persite_sq = E_persite**2

    return E_persite, E_persite_sq



    

"""
3. VISUALISING / EXPORTING THE LATTICE DATA
"""


def pbm(lattice,filename,directory):
    """
    Writes a portable bitmap image file from a given binary 
    lattice. File is saved with user-given filename to specified 
    directory.
    """

    dimensions = str(lattice.shape[1])+" "+str(lattice.shape[0])+" "
    
    # Converts given binary lattice to 0s and 1s req"d for .pbm format.
    body = ""
    for i in lattice:
        for j in i:
            if j <= 0:
                j = 0
            body += str(int(j))+" "
        body += "\n"

    # Writing the .pbm file:
    path = "./"+directory+"/"+filename
    new_img = open(path, "w")
    new_img.write("P1 \n")
    new_img.write(dimensions)    
    new_img.write(body)
    
    new_img.close()


def read_pbm(filename,directory):
    """
    Converts a .pbm file back into a numpy array. This allows arrays generated
    earlier to be reanalysed by converting the saved .pbm to an array.
    """
    
    messy_lattice = []
    
    #read in the .pbm file
    path = "./"+directory+"/"+filename
    data = open(path, "r")
    
    for line in data:
        # strip off newline characters
        line = line[:-2]
        for element in line:
            # add each element in the .pbm to list
            messy_lattice.append(element)
    data.close()
    
    # Read side length n from .pbm file, & strip off text at the beginning of file
    firstspace = messy_lattice.index(" ")
    n_as_list = messy_lattice[2:firstspace]
    n_as_str = ""
    for num in n_as_list:
        n_as_str += num
    n = int(n_as_str)
    
    if len(n_as_str) == 3:
        messy_lattice = messy_lattice[9:]
    elif len(n_as_str) == 2:
        messy_lattice = messy_lattice[7:]
    elif len(n_as_str) == 1:
        messy_lattice = messy_lattice[5:]

    # Make linear numpy array of ones the correct length
    clean_lattice = np.ones(len(messy_lattice), dtype=np.int)
    
    # Go through the "messy lattice" list; skip over the " " entries, pick out 
    # the "0" vals and replace the corresponding array vals with -1.
    # i "tracks" iteration over messy_lattice; a "tracks" index of new clean_lattice.
    i = 0
    a = 0
    while i < len(messy_lattice):
        if messy_lattice[i] != " ":
            if messy_lattice[i] == "0":
                clean_lattice[a] = -1
            a += 1
        i += 1

    # Crop the extra 1s off the end of clean_lattice
    clean_lattice = clean_lattice[:a]
    # Reform a 2D lattice with side n from the 1D array
    lattice = np.reshape(clean_lattice, (n,n))
    
    return lattice


def gif_gen(filenames,directory,savename):
    """
    Generate a .gif from a sequence of image files. Takes a list of strings, i.e. the 
    names of the image files.
    """
    
    frames = []

    for file in filenames:
        path = "./"+directory+"/"+file
        frames.append(imageio.imread(path))
    imageio.mimsave("./"+directory+"/"+savename+".gif", frames)
    

def parse_input(from_bash) :
    """
    Take an input string (from bash script), parse it and produce a tuple of the required
    variables, i.e. directory name, h_list and T_list.
    """
    
    print(from_bash)
    
    # Parse the input string for the index of the separator [
    breaks = [index for index, char in enumerate(from_bash) if char == "["]

    # Split the input string into three variables using the separator index (all strings)
    directory = str(from_bash[:breaks[0]])
    n = int(from_bash[breaks[0]+1:breaks[1]])

    # Build a list of floats from the comma-separated magnetic field values h
    h_list_elements = from_bash[breaks[1]+1:breaks[2]]
    h_breaks = [index for index, char in enumerate(h_list_elements) if char == ","]
    h_list = []
    for w in range(0,len(h_breaks)-1):
        h = h_list_elements[h_breaks[w]+1:h_breaks[w+1]]
        h_list.append(float(h))

    # Build a list of floats from the comma-separated magnetic field values T
    T_list_elements = from_bash[breaks[2]+1:]
    T_breaks = [index for index, char in enumerate(T_list_elements) if char == ","]
    T_list = []
    for w in range(0,len(T_breaks)-1):
        T = T_list_elements[T_breaks[w]+1:T_breaks[w+1]]
        T = float(T)
        T_list.append(T)

    return directory, n, h_list, T_list
