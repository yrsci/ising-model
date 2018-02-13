#!/bin/bash


printf "\n*** The Ising Model in Python 3 *** \n          by Yvonne Ryan       \n"


###
### 1. Creating new directory, choosing side length & dimension
###


# Generate a random 5-integer suffix for new directory based on time
seconds=`date +%s`
suffix=${seconds:4:${#seconds}}


# If not already entered as first variable, prompt user for a dir name & make new dir
if [ -z $1 ]; then
    printf "\nEnter a base name for new directory (files will be saved here): \n"
    read directory
else
    directory=$1
fi

mkdir $directory$suffix


# Test whether the directory was created successfully
if [ $? -eq 0 ]; then
    printf "\nSuccessfully created directory ./$directory$suffix/ \n"
else
    printf "\nCould not create directory $directory$suffix \n."
    exit 1
fi



# If not already entered as second variable, prompt user for desired lattice side length
if [ -z $2 ]; then
    printf "\nChoose the desired side length (type the number): \n8 \n16 \n32 \n64 \n128 \n"
    read n
else
    n=$2
fi


###
### 2. Defining Magnetic Field Values
###

# Define default magnetic field range; cycles from +1 to -1 to +1
default_h=1.,0.8,0.6,0.4,0.3,0.2,0.1,0.05,-0.05,-0.1,-0.2,-0.3,-0.4,-0.6,-0.8,-1.0,-0.8,-0.6,-0.4,-0.3,-0.2,-0.1,-0.05,0.05,0.1,0.2,0.3,0.4,0.6,0.8,1.0

# Prompt for choice between h=0, default h list or custom vals
printf "\nProceed with h = 0? y/n \n"
read h_choice
    
if [ $h_choice == "y" ]; then
    printf "\nProceeding with h = 0.\n"
    field=0
elif [ $h_choice == "n" ]; then
    printf "\nProceed with the following default list of h values? y/n \n" 
    printf "$default_h \n"
    read hlist_choice
    
    if [ $hlist_choice == "y" ]; then
        printf "\nProceeding with default h values."
        field=$default_h
    elif [ $hlist_choice == "n" ]; then    
        printf "\nEnter a sequence of custom values for h (comma separated). \n"
        read custom_field
        field=$custom_field
        printf "\nProceeding with the following custom list of h values: \n $field"
    fi
fi


###
### 3. Defining Temperature Values
###

default_T=1.000,1.250,1.500,1.750,1.850,1.950,2.000,2.033,2.066,2.100,2.133,2.166,2.200,2.220,2.240,2.260,2.270,2.280,2.300,2.320,2.340,2.360,2.380,2.400,2.420,2.440,2.460,2.480,2.500,2.550,2.600,2.650,2.700,2.750,2.800,2.850,2.900,3.000,4.000,5.000

# Prompt for choice between default temp list or custom vals
printf "\nProceed with the following default list of T values? y/n \n" 
printf "$default_T \n"
read T_choice

if [ $T_choice == "y" ]; then
    printf "\nProceeding with default T values. \n"
    T_list=$default_T
elif [ $T_choice == "n" ]; then
    printf "\nEnter a sequence of custom values for T (comma separated). \n" 
    read custom_T
    T_list=$custom_T
fi


###
### 4. Running Python Script
###

# Print the parameters for user prompt for choice to run / not run the simulation script
printf "\nIsing model simulation will be run with the following values: \n"
printf "h = $field \n"
printf "T = $T_list \n"
printf "\nProceed with simulation? y/n \n"
read sim_choice

# Add commas at start and end of lists to make parsing in Python easier
field=,$field,
T_list=,$T_list,

# If user selects y, run program
if [ $sim_choice == "y" ]; then
    printf "\nBeginning simulation... \n\n"
    printf "$directory$suffix[$n[$field[$T_list" | python3 ising-model.py  

    # Confirm completion / failure of the Python script
    if [ $? -eq 0 ]; then
        printf "\nSimulation successfully completed. Files saved to ./$directory$suffix/ \n" && paplay success.wav
        
        printf "\nContinue with analysis? y/n \n"
        read analysis_choice
        
        if [ $analysis_choice == "y" ]; then
            printf "\nRunning analysis script. \n"
            ./analysis.sh "$directory$suffix[0[$field[$T_list"
            
            if [ $? == 0 ]; then
                printf "\nAnalysis successfully completed. Files saved to $directory$suffix. \n"
                exit 0
            else
                printf "\nAnalysis failed.\n"
                exit 1
            fi
            
        elif [ $analysis_choice == "n" ]; then
            printf "\nExiting program. \n"
            exit 0
        fi
            
    else
        printf "\nSimulation failed. \n."
        exit 1
    fi

# If user selects n, exit program before simulation
elif [ $sim_choice == "n" ]; then
    printf "\nExiting program. \n\n"
    exit 0
fi

