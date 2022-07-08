v {xschem version=3.0.0 file_version=1.2 }
G {}
K {}
V {}
S {}
E {}
N 4020 -40 4020 10 {
lab=VSUB}
N 4120 0 4120 10 {
lab=VSUB}
N 4120 -140 4120 -60 {
lab=VDD}
N 4020 -140 4120 -140 {
lab=VDD}
N 4020 -140 4020 -100 {
lab=VDD}
N 4020 -70 4060 -70 {
lab=VDD}
N 4060 -140 4060 -70 {
lab=VDD}
N 3910 -70 3980 -70 {
lab=VG}
N 3910 -80 3910 -70 {
lab=VG}
N 3910 -140 4020 -140 {
lab=VDD}
N 3810 0 3810 30 {
lab=GND}
N 4040 -160 4040 -140 {
lab=VDD}
N 3810 -180 3810 -60 {
lab=VDD}
N 3810 -180 4040 -180 {
lab=VDD}
N 4040 -180 4040 -160 {
lab=VDD}
N 4020 10 4120 10 {
lab=VSUB}
C {devices/vsource.sym} 3810 -30 0 0 {name=Vdd value=1.8}
C {devices/vsource.sym} 4120 -30 0 0 {name=VSD value=VSDvalue
}
C {devices/gnd.sym} 3810 30 0 0 {name=l3 lab=GND}
C {sky130_fd_pr/pfet_01v8.sym} 4000 -70 0 0 {name=M1
L=TranL
W=TranW
nf=1
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {devices/vsource.sym} 3910 -110 0 0 {name=VSG value=VSGvalue
}
C {sky130_fd_pr/corner.sym} 4400 -200 0 0 {name=CORNER only_toplevel=false corner=tt}
C {devices/lab_pin.sym} 3990 -140 1 0 {name=l1 sig_type=std_logic lab=VDD}
C {devices/lab_pin.sym} 3940 -70 3 0 {name=l4 sig_type=std_logic lab=VG}
C {devices/lab_pin.sym} 4070 10 1 0 {name=l2 sig_type=std_logic lab=VSUB
}
