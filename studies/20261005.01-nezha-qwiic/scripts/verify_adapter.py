#!/usr/bin/env python3
"""Independent checks of the saved CAD and exported files, not the generator."""
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET
import pcbnew as p

root=Path(__file__).resolve().parents[1]
b=p.LoadBoard(str(root/'design/nezha-qwiic.kicad_pcb'))
fp={f.GetReference():f for f in b.GetFootprints()}
expected={
 ('J1','1'):'/GND',('J1','2'):'/+3V3',('J1','3'):'/SCL_JACK',('J1','4'):'/SDA',
 ('J2','1'):'/GND',('J2','2'):'/+3V3',('J2','3'):'/SDA',('J2','4'):'/SCL',
 ('J3','1'):'/GND',('J3','2'):'/+3V3',('J3','3'):'/SDA',('J3','4'):'/SCL',
 ('R1','1'):'/SCL',('R1','2'):'/SCL_JACK'}
actual={(f.GetReference(),a.GetNumber()):a.GetNetname() for f in fp.values() for a in f.Pads() if a.GetNumber()}
assert actual==expected,(actual,expected)
sch=ET.parse(root/'checks/netlist.xml')
sch_nets={(n.attrib['ref'],n.attrib['pin']):net.attrib['name'] for net in sch.findall('.//nets/net') for n in net.findall('node')}
assert sch_nets==expected,sch_nets
assert all(not isinstance(t,p.PCB_VIA) and t.GetLayer()==p.F_Cu for t in b.GetTracks())
assert all(p.ToMM(t.GetWidth())>=.35 for t in b.GetTracks())
assert fp['J1'].GetPosition().x < fp['J2'].GetPosition().x < fp['J3'].GetPosition().x
holes=[]
for ref in ['H1','H2']:
 a=list(fp[ref].Pads())[0]
 assert a.GetAttribute()==p.PAD_ATTRIB_NPTH
 assert p.ToMM(a.GetDrillSize().x)==3.0 and p.ToMM(a.GetDrillSize().y)==3.0
 holes.append([round(p.ToMM(a.GetPosition().x)-50,3),round(p.ToMM(a.GetPosition().y)-50,3)])
assert holes==[[4,3],[40,21]],holes
for ref in ['J1','J2','J3','R1']:
 assert all(a.GetAttribute()==p.PAD_ATTRIB_SMD for a in fp[ref].Pads())
# Check the physical male pin pitch along the header centerline; alternating
# solder tails must not be mistaken for a staggered two-row pin connector.
hp=sorted(p.ToMM(a.GetPosition().y) for a in fp['J2'].Pads())
assert all(abs(b-a-2.54)<1e-6 for a,b in zip(hp,hp[1:]))
drill=(root/'exports/milling/nezha-qwiic-NPTH.drl').read_text()
assert 'T1C3.000' in drill,drill
hits=re.findall(r'^X(-?[0-9.]+)Y(-?[0-9.]+)$',drill,re.M)
assert sorted((float(x),float(y)) for x,y in hits)==[(4.0,-3.0),(40.0,-21.0)],hits
for path in ['exports/milling/nezha-qwiic-F_Cu.gtl','exports/milling/nezha-qwiic-Edge_Cuts.gm1']:
 s=(root/path).read_text();assert '%MOMM*%' in s
 assert not any(x in s for x in ['%TF','%TA','%TO','%TD']),path
drc=json.loads((root/'checks/drc.json').read_text())
assert not any(drc[k] for k in ['violations','unconnected_items','schematic_parity'])
erc=json.loads((root/'checks/erc.json').read_text())
assert not any(s['violations'] for s in erc['sheets'])
result={'status':'PASS','board_mm':[44,24],'copper':'F.Cu only','vias':0,'holes_diameter_mm':3.0,'holes_xy_mm':holes,'header_pitch_mm':2.54,'erc_violations':0,'drc_violations':0,'unconnected_items':0,'schematic_parity_issues':0,'checks':['saved CAD versus independent pin table','exported schematic netlist versus independent pin table','SMT-only components','no vias or bottom tracks','header between connectors','3 mm NPTH drill tools and locations','RS-274X Gerber compatibility','ERC and DRC including schematic parity'],'limitation':'No physical prototype, cable continuity measurement, or on-machine cutting trial has been performed.'}
(root/'checks/validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
