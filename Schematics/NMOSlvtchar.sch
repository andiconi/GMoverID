v {xschem version=3.0.0 file_version=1.2 }
G {}
K {}
V {}
S {}
E {}
N 3910 0 3910 30 {
lab=GND}
N 4020 -70 4050 -70 {
lab=GND}
N 4050 -70 4050 -30 {
lab=GND}
N 4020 -30 4050 -30 {
lab=GND}
N 4120 0 4120 30 {
lab=GND}
N 4120 -130 4120 -60 {
lab=VD}
N 4020 -130 4120 -130 {
lab=VD}
N 4020 -130 4020 -100 {
lab=VD}
N 3910 -70 3910 -60 {
lab=VG}
N 3910 -70 3980 -70 {
lab=VG}
N 4020 40 4020 50 {
lab=GND}
N 4020 -40 4020 -30 {
lab=GND}
N 4020 -30 4020 50 {
lab=GND}
C {devices/vsource.sym} 3910 -30 0 0 {name=Vgs 
value= "dc VGSvalue ac 1 0"
}
C {devices/vsource.sym} 4120 -30 0 0 {name=VDS value=VDSvalue
}
C {devices/gnd.sym} 4020 50 0 0 {name=l1 lab=GND}
C {devices/gnd.sym} 3910 30 0 0 {name=l2 lab=GND}
C {devices/gnd.sym} 4120 30 0 0 {name=l3 lab=GND}
C {devices/lab_pin.sym} 3940 -70 1 0 {name=l4 sig_type=std_logic lab=VG}
C {devices/lab_pin.sym} 4060 -130 1 0 {name=l5 sig_type=std_logic lab=VD}
C {sky130_fd_pr/corner.sym} 4210 -230 0 0 {name=CORNER only_toplevel=false corner=tt}
C {sky130_fd_pr/nfet_01v8_lvt.sym} 4000 -70 0 0 {name=M1
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
model=nfet_01v8_lvt
spiceprefix=X
}
