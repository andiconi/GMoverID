import ngspyce
import numpy as np
import shutil
import os
#This file will do a complete charecterization of a typical NMOS and PMOS Charecterization circuit

# # todo
# export to table

print("Ensure No Spice in XSchem Schematic")

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


##########################################
#             VSD Section                #
##########################################

VGS = round(VSGNum, 5)
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
filedata = filedata.replace( 'VSGvalue', str(VGS))

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


os.remove("temp.spice") 
print("Done")