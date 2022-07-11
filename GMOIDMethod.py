import ngspyce
import numpy as np
import shutil
import os
import pandas as pd
#This file will do a complete charecterization of a typical NMOS and PMOS Charecterization circuit

# # todo
# export to table

print("Ensure No Spice in XSchem Schematic")
shutil.copy("Tables/Table.csv", "Tables/out.csv")
Table = pd.read_csv("Tables/out.csv")

# USER Varibles
# desiredValue = float(input("Enter Desired GM/ID: "))
# calculatedgm = float(input("Enter Calculated GM (10^-6): "))
# transistorL = float(input("Enter Transistor Length (10^-6): "))
desiredValue = 15
calculatedgm = 314.16
transistorL = 0.26

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

FILENAME = "Netlists/NMOSchar.spice"
#must end in a \n
commands = [
"."+ sweep +"\n",
".save @m.xm1.msky130_fd_pr__nfet_01v8[id]\n",
".save @m.xm1.msky130_fd_pr__nfet_01v8[gm]\n",
".save @m.xm1.msky130_fd_pr__nfet_01v8[w]\n",
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
ngspyce.cmd("gm = @m.xm1.msky130_fd_pr__nfet_01v8[gm]")
ngspyce.cmd("id = @m.xm1.msky130_fd_pr__nfet_01v8[id]")
ngspyce.cmd("w = @m.xm1.msky130_fd_pr__nfet_01v8[w]")
ngspyce.cmd("gmoid = gm/id")
ngspyce.cmd("JW = id/w")
ngspyce.cmd("write Simulations/JWsim.raw all")

#obtain vectors
VGS = ngspyce.vector('v(v-sweep)')
GM = ngspyce.vector('@m.xm1.msky130_fd_pr__nfet_01v8[gm]')
ID = ngspyce.vector('@m.xm1.msky130_fd_pr__nfet_01v8[id]')
W = ngspyce.vector('@m.xm1.msky130_fd_pr__nfet_01v8[w]')

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
".save @m.xm1.msky130_fd_pr__nfet_01v8[id]\n",
".save @m.xm1.msky130_fd_pr__nfet_01v8[gm]\n",
".save @m.xm1.msky130_fd_pr__nfet_01v8[w]\n",
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
ngspyce.cmd("gm = @m.xm1.msky130_fd_pr__nfet_01v8[gm]")
ngspyce.cmd("id = @m.xm1.msky130_fd_pr__nfet_01v8[id]")
ngspyce.cmd("write Simulations/vgssim.raw all")

#obtain vectors
VGS = ngspyce.vector('v(v-sweep)')
GM = ngspyce.vector('@m.xm1.msky130_fd_pr__nfet_01v8[gm]')
ID = ngspyce.vector('@m.xm1.msky130_fd_pr__nfet_01v8[id]')

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
".save @m.xm1.msky130_fd_pr__nfet_01v8[id]\n",
".save @m.xm1.msky130_fd_pr__nfet_01v8[gm]\n",
".save @m.xm1.msky130_fd_pr__nfet_01v8[gds]\n",
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
ngspyce.cmd("gm = @m.xm1.msky130_fd_pr__nfet_01v8[gm]")
ngspyce.cmd("id = @m.xm1.msky130_fd_pr__nfet_01v8[id]")
ngspyce.cmd("gds = @m.xm1.msky130_fd_pr__nfet_01v8[gds]")
ngspyce.cmd("ro = 1/gds")
ngspyce.cmd("write Simulations/vdssim.raw all")

#obtain vectors
VDS = ngspyce.vector('v(v-sweep)')
GM = ngspyce.vector('@m.xm1.msky130_fd_pr__nfet_01v8[gm]')
ID = ngspyce.vector('@m.xm1.msky130_fd_pr__nfet_01v8[id]')
GDS = ngspyce.vector('@m.xm1.msky130_fd_pr__nfet_01v8[gds]')
#caculate other vectors
ro = 1 / GDS

# find value of vds at bias current
index = np.argmin(np.abs(np.array(ID)-(Biascurrent*1e-06)))
VDSNum = VDS[index]
roNum = ro[index]
print("VDS of NMOS = " + str(round(VDSNum, 5))) 
print("ro of NMOS = " + str(round(roNum, 5)))
print("See Raw file to choose VDS deeper in saturation")


os.remove("temp.spice") 
Table.loc[9, 'NMOS'] = str(round(VDSNum, 5)) + " V"
Table.loc[10, 'NMOS'] = str(int(roNum)) + " Ohm"
Table.loc[11, 'NMOS'] = str(roNum * (calculatedgm * 10e-6))

##########################################
#            DC Sweep Section            #
##########################################

sweep = "tran 10ns 50us"

#must end in a \n
commands = [
"."+ sweep +"\n",
".save @m.xm1.msky130_fd_pr__nfet_01v8[id]\n",
".save @m.xm1.msky130_fd_pr__nfet_01v8[cgs]\n",
".save @m.xm1.msky130_fd_pr__nfet_01v8[cgd]\n",
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

print("Simulating for NMOS Capacitences")
#open file
ngspyce.source("temp.spice")

#run ngspice sweep, inserting the code in the netlist wont run ngspice
ngspyce.cmd(sweep)
ngspyce.cmd("id = @m.xm1.msky130_fd_pr__nfet_01v8[id]")
ngspyce.cmd("cgs = @m.xm1.msky130_fd_pr__nfet_01v8[cgs]")
ngspyce.cmd("cgd = @m.xm1.msky130_fd_pr__nfet_01v8[cgd]")
ngspyce.cmd("write Simulations/Tran.raw all")
#obtain vectors
# VDS = ngspyce.vector('v(v-sweep)')
CGS = ngspyce.vector('@m.xm1.msky130_fd_pr__nfet_01v8[cgs]')
CGD = ngspyce.vector('@m.xm1.msky130_fd_pr__nfet_01v8[cgd]')
Table.loc[12, 'NMOS'] = str(round(abs(CGS[200] * 10e14) ,3))+ " fF"
Table.loc[13, 'NMOS'] = str(round(abs(CGD[200] * 10e14) ,3))+ " fF"
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

FILENAME = "Netlists/PMOSchar.spice"
sweep = "dc vsg 0.05 1.8 0.001"

#must end in a \n
commands = [
"."+ sweep +"\n",
".save @m.xm1.msky130_fd_pr__pfet_01v8[id]\n",
".save @m.xm1.msky130_fd_pr__pfet_01v8[gm]\n",
".save @m.xm1.msky130_fd_pr__pfet_01v8[w]\n",
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
ngspyce.cmd("gm = @m.xm1.msky130_fd_pr__pfet_01v8[gm]")
ngspyce.cmd("id = @m.xm1.msky130_fd_pr__pfet_01v8[id]")
ngspyce.cmd("w = @m.xm1.msky130_fd_pr__pfet_01v8[w]")
ngspyce.cmd("jw = id/w")
ngspyce.cmd("gmoid = gm/id")
ngspyce.cmd("write Simulations/pJWsim.raw all")

#obtain vectors
VDS = ngspyce.vector('v(v-sweep)')
GM = ngspyce.vector('@m.xm1.msky130_fd_pr__pfet_01v8[gm]')
ID = ngspyce.vector('@m.xm1.msky130_fd_pr__pfet_01v8[id]')
W = ngspyce.vector('@m.xm1.msky130_fd_pr__pfet_01v8[w]')

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
".save @m.xm1.msky130_fd_pr__pfet_01v8[id]\n",
".save @m.xm1.msky130_fd_pr__pfet_01v8[gm]\n",
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
ngspyce.cmd("gm = @m.xm1.msky130_fd_pr__pfet_01v8[gm]")
ngspyce.cmd("id = @m.xm1.msky130_fd_pr__pfet_01v8[id]")
ngspyce.cmd("write Simulations/pvgssim.raw all")

#obtain vectors
VSG = ngspyce.vector('v(v-sweep)')
GM = ngspyce.vector('@m.xm1.msky130_fd_pr__pfet_01v8[gm]')
ID = ngspyce.vector('@m.xm1.msky130_fd_pr__pfet_01v8[id]')


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
".save @m.xm1.msky130_fd_pr__pfet_01v8[id]\n",
".save @m.xm1.msky130_fd_pr__pfet_01v8[gds]\n",
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
ngspyce.cmd("id = @m.xm1.msky130_fd_pr__pfet_01v8[id]")
ngspyce.cmd("gds = @m.xm1.msky130_fd_pr__pfet_01v8[gds]")
ngspyce.cmd("ro = 1/gds")
ngspyce.cmd("write Simulations/pvds.raw all")

#obtain vectors
VSD = ngspyce.vector('v(v-sweep)')
ID = ngspyce.vector('@m.xm1.msky130_fd_pr__pfet_01v8[id]')
GDS = ngspyce.vector('@m.xm1.msky130_fd_pr__pfet_01v8[gds]')
#caculate other vectors
ro = 1 / GDS


# find value of vsd at bias current
index = np.argmin(np.abs(np.array(ID)-(Biascurrent*1e-06)))
VSDNum = VSD[index]
roNum = ro[index]
print("VDS of PMOS = " + str(round(VSDNum, 5)))
print("ro of PMOS = " + str(round(roNum, 5)))
print("See Raw file to choose VSD deeper in saturation")

Table.loc[9, 'PMOS'] = str(round(VSDNum, 5)) + " V"
Table.loc[10, 'PMOS'] = str(int(roNum)) + " Ohm"
Table.loc[11, 'PMOS'] = str(roNum * (calculatedgm * 10e-6))
os.remove("temp.spice") 


##########################################
#            DC Sweep Section            #
##########################################

sweep = "tran 10ns 50us"

#must end in a \n
commands = [
"."+ sweep +"\n",
".save @m.xm1.msky130_fd_pr__pfet_01v8[id]\n",
".save @m.xm1.msky130_fd_pr__pfet_01v8[cgs]\n",
".save @m.xm1.msky130_fd_pr__pfet_01v8[cgd]\n",
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

print("Simulating for PMOS Capacitences")
#open file
ngspyce.source("temp.spice")

#run ngspice sweep, inserting the code in the netlist wont run ngspice
ngspyce.cmd(sweep)
ngspyce.cmd("id = @m.xm1.msky130_fd_pr__pfet_01v8[id]")
ngspyce.cmd("cgs = @m.xm1.msky130_fd_pr__pfet_01v8[cgs]")
ngspyce.cmd("cgd = @m.xm1.msky130_fd_pr__pfet_01v8[cgd]")
ngspyce.cmd("write Simulations/pTran.raw all")
#obtain vectors
# VDS = ngspyce.vector('v(v-sweep)')
CSG = ngspyce.vector('@m.xm1.msky130_fd_pr__pfet_01v8[cgs]')
CDG = ngspyce.vector('@m.xm1.msky130_fd_pr__pfet_01v8[cgd]')
Table.loc[12, 'PMOS'] = str(round(abs(CSG[200] * 10e14) ,3))+ " fF"
Table.loc[13, 'PMOS'] = str(round(abs(CDG[200] * 10e14) ,3))+ " fF"
os.remove("temp.spice") 

Table.to_csv("Tables/out.csv", index=False)
print("Done. View Charecterization in Tables/out.csv")