import ngspyce
import numpy as np
import math 
import shutil
import os
import pandas as pd
#LOW Vthreshold Version
#This file will do a complete charecterization of a typical NMOS and PMOS Charecterization circuit
print("Ensure No Spice in XSchem Schematic")
shutil.copy("Tables/Table.csv", "Tables/outLVT.csv")
Table = pd.read_csv("Tables/outLVT.csv")

# USER Varibles (Can be changed maunally or at every run)
# desiredValue = float(input("Enter Desired GM/ID: "))
# calculatedgm = float(input("Enter Calculated GM (10^-6): "))
# transistorL = float(input("Enter Transistor Length (10^-6): "))
desiredValue = 12
calculatedgm = 314.16
transistorL = 0.36

#quick calculations
vstar = 2/desiredValue
Biascurrent = calculatedgm/desiredValue
#Display to user
print("V* = " + str(round(vstar, 4)))
print("ID = " + str(round(Biascurrent, 4)))

#Write to CSV
Table.loc[0, 'NMOS'] = '1.8V'
Table.loc[0, 'PMOS'] = '1.8V'
Table.loc[1, 'NMOS'] = str(transistorL) + " um"
Table.loc[1, 'PMOS'] = str(transistorL) + " um"
Table.loc[2, 'NMOS'] = str(desiredValue)
Table.loc[2, 'PMOS'] = str(desiredValue)
Table.loc[3, 'NMOS'] = str(round(vstar, 3)) + " mV"
Table.loc[3, 'PMOS'] = str(round(vstar, 3)) + " mV"
Table.loc[4, 'NMOS'] = str(calculatedgm) + " uA/V"
Table.loc[4, 'PMOS'] = str(calculatedgm) + " uA/V"
Table.loc[5, 'NMOS'] = str(round(Biascurrent, 3)) + " uA"
Table.loc[5, 'PMOS'] = str(round(Biascurrent, 3)) + " uA"

##########################################
#             JW Section                 #
##########################################

sweep = "dc vgs 0.05 1.8 0.001"

FILENAME = "Netlists/NMOSlvtchar.spice"
#must end in a \n
commands = [
"."+ sweep +"\n",
".save @m.xm1.msky130_fd_pr__nfet_01v8_lvt[id]\n",
".save @m.xm1.msky130_fd_pr__nfet_01v8_lvt[gm]\n",
".save @m.xm1.msky130_fd_pr__nfet_01v8_lvt[w]\n",
".save v(vg) v(v-sweep) v(vd)\n"
]

#Copy Netlist file to edit for this simulation
shutil.copy(FILENAME, "temp.spice")

#Change Parameters
with open('temp.spice', 'r') as file :
  filedata = file.read()

# Replace the target string
filedata = filedata.replace( 'TranW', str(2.6))
filedata = filedata.replace( 'TranL', str(transistorL))
filedata = filedata.replace( 'VDSvalue', str(round(vstar, 4)))
filedata = filedata.replace( 'VGSvalue', str(round(0.7, 4)))

# Write the file out again
with open('temp.spice', 'w') as file:
  file.write(filedata)

#edit copied file
a_file = open("temp.spice", "r")
list_of_lines = a_file.readlines()
for i in range(len(list_of_lines)):
    if list_of_lines[i]  == "**** begin user architecture code\n":
        if list_of_lines[i+1] == "\n":
            list_of_lines[i+1] = "*begin commands\n" + "".join(commands) + "*end commands\n\n"
            a_file = open("temp.spice", "w")
            a_file.writelines(list_of_lines)
            break  
        else:
            print("Commands Already Added. Replacing")
            j = i + 1
            while list_of_lines[j] != "*end commands\n":
                list_of_lines.pop(j)
            list_of_lines.remove("*end commands\n")
            list_of_lines[i+1] = "*begin commands\n" + "".join(commands) + "*end commands\n\n"
            a_file = open("temp.spice", "w")
            a_file.writelines(list_of_lines)
            break 
a_file.close()

print("Simulating For Width of NMOS")
#open file
ngspyce.source('temp.spice')

#run ngspice sweep. This library runs ngspice in interactive mode. .save commands do not work hence the netlist editing
ngspyce.cmd(sweep)
ngspyce.cmd("gm = @m.xm1.msky130_fd_pr__nfet_01v8_lvt[gm]")
ngspyce.cmd("id = @m.xm1.msky130_fd_pr__nfet_01v8_lvt[id]")
ngspyce.cmd("w = @m.xm1.msky130_fd_pr__nfet_01v8_lvt[w]")
ngspyce.cmd("gmoid = gm/id")
ngspyce.cmd("JW = id/w")
ngspyce.cmd("write Simulations/LVT/JWsim.raw all")

#obtain vectors
VGS = ngspyce.vector('v(v-sweep)')
GM = ngspyce.vector('@m.xm1.msky130_fd_pr__nfet_01v8_lvt[gm]')
ID = ngspyce.vector('@m.xm1.msky130_fd_pr__nfet_01v8_lvt[id]')
W = ngspyce.vector('@m.xm1.msky130_fd_pr__nfet_01v8_lvt[w]')

#caculate other vectors
GMOID = GM / ID
JW = ID / W

# Calculate closest Value to desiredValue
index = np.argmin(np.abs(np.array(GMOID)-desiredValue))

widthNUM = Biascurrent/JW[index]
print("Width of NMOS = " + str(round(widthNUM, 2)))

# Cleanup
os.remove("temp.spice") 
Table.loc[6, 'NMOS'] = str(round(JW[index], 3)) + " A"
Table.loc[7, 'NMOS'] = str(round(widthNUM, 2)) + " um"
##########################################
#             VGS Section                #
##########################################

width = str(round(widthNUM, 4))
sweep = "dc vgs 0.05 1.8 0.001"

#must end in a \n
commands = [
"."+ sweep +"\n",
".save @m.xm1.msky130_fd_pr__nfet_01v8_lvt[id]\n",
".save @m.xm1.msky130_fd_pr__nfet_01v8_lvt[gm]\n",
".save v(vg) v(v-sweep) v(vd)\n"
]

#Copy Netlist file to edit for this simulation
shutil.copy(FILENAME, "temp.spice")

#Change Width
with open('temp.spice', 'r') as file :
  filedata = file.read()

# Replace the target string
filedata = filedata.replace( 'TranW', width)
filedata = filedata.replace( 'TranL', str(transistorL))
filedata = filedata.replace( 'VDSvalue', str(round(vstar, 4)))
filedata = filedata.replace( 'VGSvalue', str(0.7))

# Write the file out again
with open('temp.spice', 'w') as file:
  file.write(filedata)

#edit copied file
a_file = open("temp.spice", "r")
list_of_lines = a_file.readlines()
for i in range(len(list_of_lines)):
    if list_of_lines[i]  == "**** begin user architecture code\n":
        if list_of_lines[i+1] == "\n":
            list_of_lines[i+1] = "*begin commands\n" + "".join(commands) + "*end commands\n\n"
            a_file = open("temp.spice", "w")
            a_file.writelines(list_of_lines)
            break  
        else:
            print("Commands Already Added. Replacing")
            j = i + 1
            while list_of_lines[j] != "*end commands\n":
                list_of_lines.pop(j)
            list_of_lines.remove("*end commands\n")
            list_of_lines[i+1] = "*begin commands\n" + "".join(commands) + "*end commands\n\n"
            a_file = open("temp.spice", "w")
            a_file.writelines(list_of_lines)
            break 
a_file.close()


print("Simulating For VGS of NMOS")

#open file
ngspyce.source("temp.spice")

#run ngspice sweep
ngspyce.cmd(sweep)

#additional commands
ngspyce.cmd("gm = @m.xm1.msky130_fd_pr__nfet_01v8_lvt[gm]")
ngspyce.cmd("id = @m.xm1.msky130_fd_pr__nfet_01v8_lvt[id]")
ngspyce.cmd("write Simulations/LVT/vgssim.raw all")

#obtain vectors
VGS = ngspyce.vector('v(v-sweep)')
GM = ngspyce.vector('@m.xm1.msky130_fd_pr__nfet_01v8_lvt[gm]')
ID = ngspyce.vector('@m.xm1.msky130_fd_pr__nfet_01v8_lvt[id]')

# find value of vgs at bias current
index = np.argmin(np.abs(np.array(ID)-(Biascurrent*1e-06)))
VGSNum = VGS[index]
print("VGS of NMOS = " + str(round(VGSNum, 5)))


os.remove("temp.spice") 

Table.loc[8, 'NMOS'] = str(round(VGSNum, 5)) + " V"
##########################################
#             VDS Section                #
##########################################

VGS = round(VGSNum, 5)
#enter sweep command here
sweep = "dc vds 0.05 1.8 0.001"

#must end in a \n
commands = [
"."+ sweep +"\n",
".save @m.xm1.msky130_fd_pr__nfet_01v8_lvt[id]\n",
".save @m.xm1.msky130_fd_pr__nfet_01v8_lvt[gm]\n",
".save @m.xm1.msky130_fd_pr__nfet_01v8_lvt[gds]\n",
".save v(vg) v(v-sweep) v(vd)\n"
]

#Copy Netlist file to edit for this simulation
shutil.copy(FILENAME, "temp.spice")

#Change Width
with open('temp.spice', 'r') as file :
  filedata = file.read()

# Replace the target string
filedata = filedata.replace( 'TranW', width)
filedata = filedata.replace( 'TranL', str(transistorL))
filedata = filedata.replace( 'VDSvalue', str(round(vstar, 4)))
filedata = filedata.replace( 'VGSvalue', str(VGS))

# Write the file out again
with open('temp.spice', 'w') as file:
  file.write(filedata)

#Editing Copied File
a_file = open("temp.spice", "r")
list_of_lines = a_file.readlines()
for i in range(len(list_of_lines)):
    if list_of_lines[i]  == "**** begin user architecture code\n":
        if list_of_lines[i+1] == "\n":
            list_of_lines[i+1] = "*begin commands\n" + "".join(commands) + "*end commands\n\n"
            a_file = open("temp.spice", "w")
            a_file.writelines(list_of_lines)
            break  
        else:
            print("Commands Already Added. Replacing")
            j = i + 1
            while list_of_lines[j] != "*end commands\n":
                list_of_lines.pop(j)
            list_of_lines.remove("*end commands\n")
            list_of_lines[i+1] = "*begin commands\n" + "".join(commands) + "*end commands\n\n"
            a_file = open("temp.spice", "w")
            a_file.writelines(list_of_lines)
            break 
a_file.close()

print("Simulating For VDS of NMOS")

#open file
ngspyce.source("temp.spice")

#run ngspice sweep
ngspyce.cmd(sweep)

#Additional commands
ngspyce.cmd("gm = @m.xm1.msky130_fd_pr__nfet_01v8_lvt[gm]")
ngspyce.cmd("id = @m.xm1.msky130_fd_pr__nfet_01v8_lvt[id]")
ngspyce.cmd("gds = @m.xm1.msky130_fd_pr__nfet_01v8_lvt[gds]")
ngspyce.cmd("ro = 1/gds")
ngspyce.cmd("write Simulations/LVT/vdssim.raw all")

#obtain vectors
VDS = ngspyce.vector('v(v-sweep)')
GM = ngspyce.vector('@m.xm1.msky130_fd_pr__nfet_01v8_lvt[gm]')
ID = ngspyce.vector('@m.xm1.msky130_fd_pr__nfet_01v8_lvt[id]')
GDS = ngspyce.vector('@m.xm1.msky130_fd_pr__nfet_01v8_lvt[gds]')
#caculate other vectors
ro = 1 / GDS

# find value of vds at bias current
index = np.argmin(np.abs(np.array(ID)-(Biascurrent*1e-06)))
VDSNum = VDS[index]
roNum = ro[index]
gmnro = int(roNum) * (calculatedgm * 1e-6)
print("VDS of NMOS = " + str(round(VDSNum, 5))) 
print("ro of NMOS = " + str(round(roNum, 5)))
print("Intrinsic Gain of NMOS = " + str(round(gmnro, 5)))
print("See Raw file to choose VDS deeper in saturation")


os.remove("temp.spice") 
Table.loc[9, 'NMOS'] = str(round(VDSNum, 5)) + " V"
Table.loc[10, 'NMOS'] = str(int(roNum)) + " Ohm"
Table.loc[11, 'NMOS'] = str(gmnro)

##########################################
#            DC Sweep Section            #
##########################################

sweep = "tran 10ns 50us"

#must end in a \n
commands = [
"."+ sweep +"\n",
".save @m.xm1.msky130_fd_pr__nfet_01v8_lvt[id]\n",
".save @m.xm1.msky130_fd_pr__nfet_01v8_lvt[cgs]\n",
".save @m.xm1.msky130_fd_pr__nfet_01v8_lvt[cgd]\n",
".save @m.xm1.msky130_fd_pr__nfet_01v8_lvt[cgg]\n",
".save v(vg) v(v-sweep) v(vd)\n"
]


#Copy Netlist file to edit for this simulation

shutil.copy(FILENAME, "temp.spice")

#Change Width
with open('temp.spice', 'r') as file :
  filedata = file.read()

    # Replace the target string
filedata = filedata.replace( 'TranW', width)
filedata = filedata.replace( 'TranL', str(transistorL))
filedata = filedata.replace( 'VDSvalue', str(round(VDSNum, 5)))
filedata = filedata.replace( 'VGSvalue', str(VGS))

    # Write the file out again
with open('temp.spice', 'w') as file:
  file.write(filedata)

#have to insert sweep into file becuase it does not work other wise
a_file = open("temp.spice", "r")
list_of_lines = a_file.readlines()
for i in range(len(list_of_lines)):
    if list_of_lines[i]  == "**** begin user architecture code\n":
        if list_of_lines[i+1] == "\n":
            list_of_lines[i+1] = "*begin commands\n" + "".join(commands) + "*end commands\n\n"
            a_file = open("temp.spice", "w")
            a_file.writelines(list_of_lines)
            break  
        else:
            print("Commands Already Added. Replacing")
            j = i + 1
            while list_of_lines[j] != "*end commands\n":
                list_of_lines.pop(j)
            list_of_lines.remove("*end commands\n")
            list_of_lines[i+1] = "*begin commands\n" + "".join(commands) + "*end commands\n\n"
            a_file = open("temp.spice", "w")
            a_file.writelines(list_of_lines)
            break 
a_file.close()

print("Simulating for NMOS Capacitences and FT")
#open file
ngspyce.source("temp.spice")

#run ngspice sweep, inserting the code in the netlist wont run ngspice
ngspyce.cmd(sweep)
ngspyce.cmd("id = @m.xm1.msky130_fd_pr__nfet_01v8_lvt[id]")
ngspyce.cmd("cgs = @m.xm1.msky130_fd_pr__nfet_01v8_lvt[cgs]")
ngspyce.cmd("cgd = @m.xm1.msky130_fd_pr__nfet_01v8_lvt[cgd]")
ngspyce.cmd("write Simulations/LVT/Tran.raw all")
#obtain vectors
CGS = ngspyce.vector('@m.xm1.msky130_fd_pr__nfet_01v8_lvt[cgs]')
CGD = ngspyce.vector('@m.xm1.msky130_fd_pr__nfet_01v8_lvt[cgd]')
CGG = ngspyce.vector('@m.xm1.msky130_fd_pr__nfet_01v8_lvt[cgg]')
#Estimate FT through capacitences
FT = (calculatedgm * 1e-6)/(2*math.pi*(abs(CGD[200])+abs(CGS[200]))) * 1e-9
print("CGG of NMOS = " + str(round(abs(CGG[200] * 1e15) ,3))+ " fF")
print("CGS of NMOS = " + str(round(abs(CGS[200] * 1e15) ,3))+ " fF")
print("CGD of NMOS = " + str(round(abs(CGD[200] * 1e15) ,3))+ " fF")
print("FT of NMOS = " + str(round(FT ,3)) + " GHz")

Table.loc[12, 'NMOS'] = str(round(abs(CGG[200] * 1e15) ,3))+ " fF"
Table.loc[13, 'NMOS'] = str(round(abs(CGS[200] * 1e15) ,3))+ " fF"
Table.loc[14, 'NMOS'] = str(round(abs(CGD[200] * 1e15) ,3))+ " fF"
Table.loc[15, 'NMOS'] = str(round(FT ,3)) + " GHz"

os.remove("temp.spice") 
print("NMOS Finished")
print("\n")
##########################################
##########################################
#             PMOS Section               #
##########################################
##########################################

##########################################
#             JW Section                 #
##########################################

FILENAME = "Netlists/PMOSlvtchar.spice"
sweep = "dc vsg 0.05 1.8 0.001"

#must end in a \n
commands = [
"."+ sweep +"\n",
".save @m.xm1.msky130_fd_pr__pfet_01v8_lvt[id]\n",
".save @m.xm1.msky130_fd_pr__pfet_01v8_lvt[gm]\n",
".save @m.xm1.msky130_fd_pr__pfet_01v8_lvt[w]\n",
".save v(vg) v(v-sweep) v(vd)\n"
]


#Copy Netlist file to edit for this simulation

shutil.copy(FILENAME, "temp.spice")

with open('temp.spice', 'r') as file :
  filedata = file.read()

# Replace the target string
filedata = filedata.replace( 'TranW', str(2.6))
filedata = filedata.replace( 'TranL', str(transistorL))
filedata = filedata.replace( 'VSDvalue', str(round(vstar, 4)))
filedata = filedata.replace( 'VSGvalue', str(round(0.7, 4)))

# Write the file out again
with open('temp.spice', 'w') as file:
  file.write(filedata)

#have to insert sweep into file becuase it does not work other wise
a_file = open("temp.spice", "r")
list_of_lines = a_file.readlines()
for i in range(len(list_of_lines)):
    if list_of_lines[i]  == "**** begin user architecture code\n":
        if list_of_lines[i+1] == "\n":
            list_of_lines[i+1] = "*begin commands\n" + "".join(commands) + "*end commands\n\n"
            a_file = open("temp.spice", "w")
            a_file.writelines(list_of_lines)
            break  
        else:
            print("Commands Already Added. Replacing")
            j = i + 1
            while list_of_lines[j] != "*end commands\n":
                list_of_lines.pop(j)
            list_of_lines.remove("*end commands\n")
            list_of_lines[i+1] = "*begin commands\n" + "".join(commands) + "*end commands\n\n"
            a_file = open("temp.spice", "w")
            a_file.writelines(list_of_lines)
            break 
a_file.close()

print("Simulating for Width of PMOS")
#open file
ngspyce.source("temp.spice")

#run ngspice sweep
ngspyce.cmd(sweep)
ngspyce.cmd("gm = @m.xm1.msky130_fd_pr__pfet_01v8_lvt[gm]")
ngspyce.cmd("id = @m.xm1.msky130_fd_pr__pfet_01v8_lvt[id]")
ngspyce.cmd("w = @m.xm1.msky130_fd_pr__pfet_01v8_lvt[w]")
ngspyce.cmd("jw = id/w")
ngspyce.cmd("gmoid = gm/id")
ngspyce.cmd("write Simulations/LVT/pJWsim.raw all")

#obtain vectors
VDS = ngspyce.vector('v(v-sweep)')
GM = ngspyce.vector('@m.xm1.msky130_fd_pr__pfet_01v8_lvt[gm]')
ID = ngspyce.vector('@m.xm1.msky130_fd_pr__pfet_01v8_lvt[id]')
W = ngspyce.vector('@m.xm1.msky130_fd_pr__pfet_01v8_lvt[w]')

GMOID = GM/ID
JW = ID/W
index = np.argmin(np.abs(np.array(GMOID)-desiredValue))


widthNUM = Biascurrent/JW[index]
print("Width of PMOS = " + str(round(widthNUM, 2)))

os.remove("temp.spice") 
Table.loc[6, 'PMOS'] = str(round(JW[index], 3)) + " A"
Table.loc[7, 'PMOS'] = str(round(widthNUM, 2)) + " um"

##########################################
#             VSG Section                #
##########################################



width = str(round(widthNUM, 2))
#enter sweep command here
sweep = "dc vsg 0.05 1.8 0.001"

#must end in a \n
commands = [
"."+ sweep +"\n",
".save @m.xm1.msky130_fd_pr__pfet_01v8_lvt[id]\n",
".save @m.xm1.msky130_fd_pr__pfet_01v8_lvt[gm]\n",
".save v(vg) v(v-sweep) v(vd)\n"
]


#Copy Netlist file to edit for this simulation
shutil.copy(FILENAME, "temp.spice")

#Change Width
with open('temp.spice', 'r') as file :
  filedata = file.read()

# Replace the target string
filedata = filedata.replace( 'TranW', width)
filedata = filedata.replace( 'TranL', str(transistorL))
filedata = filedata.replace( 'VSDvalue', str(round(vstar, 4)))
filedata = filedata.replace( 'VSGvalue', str(0.7))

    # Write the file out again
with open('temp.spice', 'w') as file:
  file.write(filedata)

#edit copied file
a_file = open("temp.spice", "r")
list_of_lines = a_file.readlines()
for i in range(len(list_of_lines)):
    if list_of_lines[i]  == "**** begin user architecture code\n":
        if list_of_lines[i+1] == "\n":
            list_of_lines[i+1] = "*begin commands\n" + "".join(commands) + "*end commands\n\n"
            a_file = open("temp.spice", "w")
            a_file.writelines(list_of_lines)
            break  
        else:
            print("Commands Already Added. Replacing")
            j = i + 1
            while list_of_lines[j] != "*end commands\n":
                list_of_lines.pop(j)
            list_of_lines.remove("*end commands\n")
            list_of_lines[i+1] = "*begin commands\n" + "".join(commands) + "*end commands\n\n"
            a_file = open("temp.spice", "w")
            a_file.writelines(list_of_lines)
            break 
a_file.close()


print("Simulating for VGS of PMOS")
#open file
ngspyce.source("temp.spice")

#run ngspice sweep, inserting the code in the netlist wont run ngspice
ngspyce.cmd(sweep)

#additional commands
ngspyce.cmd("gm = @m.xm1.msky130_fd_pr__pfet_01v8_lvt[gm]")
ngspyce.cmd("id = @m.xm1.msky130_fd_pr__pfet_01v8_lvt[id]")
ngspyce.cmd("write Simulations/LVT/pvgssim.raw all")

#obtain vectors
VSG = ngspyce.vector('v(v-sweep)')
GM = ngspyce.vector('@m.xm1.msky130_fd_pr__pfet_01v8_lvt[gm]')
ID = ngspyce.vector('@m.xm1.msky130_fd_pr__pfet_01v8_lvt[id]')

os.remove("temp.spice") 

index = np.argmin(np.abs(np.array(ID)-(Biascurrent*1e-06)))
VSGNum = VSG[index]
print("VSG of NMOS = " + str(round(VSGNum, 5)))

Table.loc[8, 'PMOS'] = str(round(VSGNum, 5)) + " V"
##########################################
#             VSD Section                #
##########################################

VSG = round(VSGNum, 5)
sweep = "dc vsd 0.05 1.8 0.001"

#must end in a \n
commands = [
"."+ sweep +"\n",
".save @m.xm1.msky130_fd_pr__pfet_01v8_lvt[id]\n",
".save @m.xm1.msky130_fd_pr__pfet_01v8_lvt[gds]\n",
".save v(vg) v(v-sweep) v(vd)\n"
]


#Copy Netlist file to edit for this simulation

shutil.copy(FILENAME, "temp.spice")

#Change Width
with open('temp.spice', 'r') as file :
  filedata = file.read()

    # Replace the target string
filedata = filedata.replace( 'TranW', width)
filedata = filedata.replace( 'TranL', str(transistorL))
filedata = filedata.replace( 'VSDvalue', str(round(vstar, 4)))
filedata = filedata.replace( 'VSGvalue', str(VSG))

    # Write the file out again
with open('temp.spice', 'w') as file:
  file.write(filedata)

#have to insert sweep into file becuase it does not work other wise
a_file = open("temp.spice", "r")
list_of_lines = a_file.readlines()
for i in range(len(list_of_lines)):
    if list_of_lines[i]  == "**** begin user architecture code\n":
        if list_of_lines[i+1] == "\n":
            list_of_lines[i+1] = "*begin commands\n" + "".join(commands) + "*end commands\n\n"
            a_file = open("temp.spice", "w")
            a_file.writelines(list_of_lines)
            break  
        else:
            print("Commands Already Added. Replacing")
            j = i + 1
            while list_of_lines[j] != "*end commands\n":
                list_of_lines.pop(j)
            list_of_lines.remove("*end commands\n")
            list_of_lines[i+1] = "*begin commands\n" + "".join(commands) + "*end commands\n\n"
            a_file = open("temp.spice", "w")
            a_file.writelines(list_of_lines)
            break 
a_file.close()

print("Simulating for VSD of PMOS")
#open file
ngspyce.source("temp.spice")

#run ngspice sweep, inserting the code in the netlist wont run ngspice
ngspyce.cmd(sweep)
ngspyce.cmd("id = @m.xm1.msky130_fd_pr__pfet_01v8_lvt[id]")
ngspyce.cmd("gds = @m.xm1.msky130_fd_pr__pfet_01v8_lvt[gds]")
ngspyce.cmd("ro = 1/gds")
ngspyce.cmd("write Simulations/LVT/pvds.raw all")

#obtain vectors
VSD = ngspyce.vector('v(v-sweep)')
ID = ngspyce.vector('@m.xm1.msky130_fd_pr__pfet_01v8_lvt[id]')
GDS = ngspyce.vector('@m.xm1.msky130_fd_pr__pfet_01v8_lvt[gds]')
#caculate other vectors
ro = 1 / GDS


# find value of vsd at bias current
index = np.argmin(np.abs(np.array(ID)-(Biascurrent*1e-06)))
VSDNum = VSD[index]
roNum = ro[index]
gmpro = roNum * (calculatedgm * 1e-6)
print("VDS of PMOS = " + str(round(VSDNum, 5)))
print("ro of PMOS = " + str(round(roNum, 5)))
print("Intrinsic Gain of PMOS = " + str(round(gmpro, 5)))
print("See Raw file to choose VSD deeper in saturation")

Table.loc[9, 'PMOS'] = str(round(VSDNum, 5)) + " V"
Table.loc[10, 'PMOS'] = str(int(roNum)) + " Ohm"
Table.loc[11, 'PMOS'] = str(gmpro)
os.remove("temp.spice") 


##########################################
#            DC Sweep Section            #
##########################################

sweep = "tran 10ns 50us"

#must end in a \n
commands = [
"."+ sweep +"\n",
".save @m.xm1.msky130_fd_pr__pfet_01v8_lvt[id]\n",
".save @m.xm1.msky130_fd_pr__pfet_01v8_lvt[cgs]\n",
".save @m.xm1.msky130_fd_pr__pfet_01v8_lvt[cgd]\n",
".save @m.xm1.msky130_fd_pr__pfet_01v8_lvt[cgg]\n",
".save v(vg) v(v-sweep) v(vd)\n"
]


#Copy Netlist file to edit for this simulation

shutil.copy(FILENAME, "temp.spice")

#Change Width
with open('temp.spice', 'r') as file :
  filedata = file.read()

    # Replace the target string
filedata = filedata.replace( 'TranW', width)
filedata = filedata.replace( 'TranL', str(transistorL))
filedata = filedata.replace( 'VSDvalue', str(round(VSDNum, 4)))
filedata = filedata.replace( 'VSGvalue', str(VSG))

    # Write the file out again
with open('temp.spice', 'w') as file:
  file.write(filedata)

#have to insert sweep into file becuase it does not work other wise
a_file = open("temp.spice", "r")
list_of_lines = a_file.readlines()
for i in range(len(list_of_lines)):
    if list_of_lines[i]  == "**** begin user architecture code\n":
        if list_of_lines[i+1] == "\n":
            list_of_lines[i+1] = "*begin commands\n" + "".join(commands) + "*end commands\n\n"
            a_file = open("temp.spice", "w")
            a_file.writelines(list_of_lines)
            break  
        else:
            print("Commands Already Added. Replacing")
            j = i + 1
            while list_of_lines[j] != "*end commands\n":
                list_of_lines.pop(j)
            list_of_lines.remove("*end commands\n")
            list_of_lines[i+1] = "*begin commands\n" + "".join(commands) + "*end commands\n\n"
            a_file = open("temp.spice", "w")
            a_file.writelines(list_of_lines)
            break 
a_file.close()

print("Simulating for PMOS Capacitences and FT")
#open file
ngspyce.source("temp.spice")

#run ngspice sweep, inserting the code in the netlist wont run ngspice
ngspyce.cmd(sweep)
ngspyce.cmd("id = @m.xm1.msky130_fd_pr__pfet_01v8_lvt[id]")
ngspyce.cmd("cgs = @m.xm1.msky130_fd_pr__pfet_01v8_lvt[cgs]")
ngspyce.cmd("cgd = @m.xm1.msky130_fd_pr__pfet_01v8_lvt[cgd]")
ngspyce.cmd("write Simulations/LVT/pTran.raw all")
#obtain vectors
CSG = ngspyce.vector('@m.xm1.msky130_fd_pr__pfet_01v8_lvt[cgs]')
CDG = ngspyce.vector('@m.xm1.msky130_fd_pr__pfet_01v8_lvt[cgd]')
CGG = ngspyce.vector('@m.xm1.msky130_fd_pr__pfet_01v8_lvt[cgg]')
FT = (calculatedgm * 1e-6)/(2*math.pi*(abs(CDG[200])+abs(CSG[200]))) * 1e-9

print("CGG of PMOS = " + str(round(abs(CGG[200] * 1e15) ,3))+ " fF")
print("CGS of PMOS = " + str(round(abs(CSG[200] * 1e15) ,3))+ " fF")
print("CGD of PMOS = " + str(round(abs(CDG[200] * 1e15) ,3))+ " fF")
print("FT of PMOS = " + str(round(FT ,3)) + " GHz")

Table.loc[12, 'PMOS'] = str(round(abs(CGG[200] * 1e15) ,3))+ " fF"
Table.loc[13, 'PMOS'] = str(round(abs(CSG[200] * 1e15) ,3))+ " fF"
Table.loc[14, 'PMOS'] = str(round(abs(CDG[200] * 1e15) ,3))+ " fF"
Table.loc[15, 'PMOS'] = str(round(FT ,3))+ " GHz"
os.remove("temp.spice") 

Table.to_csv("Tables/outLVT.csv", index=False)
print("Done. View Charecterization in Tables/outLVT.csv")