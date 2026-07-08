import sys, json
from datetime import datetime
sys.path.insert(0,'/home/user/Astrology-App/backend')
sys.path.insert(0,'/home/user/Astrology-App/java_harness')
from astrology.vakya_table_engine import VakyaTableEngine
import run_python_vs_ics as R
eng=VakyaTableEngine('/home/user/Astrology-App/backend/astrology/data/vakya')
LAT,LON,TZ=11.6643,78.185,5.5
S=40/3.0; PS=S/4.0
NAK=R.NAKSHATRAS
SIGN={'Mesham':0,'Rishabam':1,'Mithunam':2,'Kadakam':3,'Simmam':4,'Kanni':5,
      'Tulam':6,'Viruchigam':7,'Dhanusu':8,'Magaram':9,'Kumbam':10,'Meenam':11}
PLANETS=['Lagnam','Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']
def dms(s):
    a=s.split(':'); return int(a[0])+int(a[1])/60.0+float(a[2])/3600.0
def pada(deg):
    deg%=360;i=int(deg/S);i=26 if i>=27 else i;p=(int(deg/S*4)%4)+1;return i,p
recs=json.load(open('tests/astrology_data .json'))
out=[]
per={p:{'n':0,'gt':0,'fail':0} for p in PLANETS}
for idx,rec in enumerate(recs):
    y,m,d=R.parse_date(rec['date_of_birth']); h,mn=R.parse_time(rec['time_of_birth'])
    if h is None: continue
    try: res=eng.compute(datetime(y,m,d,h,mn),LAT,LON,TZ)
    except Exception as e: continue
    # index ICS planets (strip (R))
    icsmap={}
    for pp in rec['planetary_positions']:
        nm=pp['planet'].replace('(R)','').replace('(r)','').strip()
        icsmap[nm]=pp
    for pl in PLANETS:
        if pl not in icsmap or pl not in res: continue
        pp=icsmap[pl]
        abs_field=dms(pp['absolute_longitude']) if pp.get('absolute_longitude') else None
        rasi=pp.get('rasi',''); rlon=dms(pp['rasi_longitude']) if pp.get('rasi_longitude') else None
        # reconstruct true ICS absolute from rasi sign + rasi_longitude
        true_ics=None; corrupt=False
        if rasi in SIGN and rlon is not None:
            true_ics=SIGN[rasi]*30.0+rlon
            if abs_field is not None and abs(((abs_field-true_ics+180)%360)-180)>1.0:
                corrupt=True
        if true_ics is None: true_ics=abs_field
        if true_ics is None: continue
        engv=res[pl]['longitude']
        off=((engv-true_ics+180)%360)-180
        per[pl]['n']+=1
        # pada from ICS star_name
        icspad=None; sn=(pp.get('star_name') or '').split()[0] if pp.get('star_name') else ''
        ni=R.nak_to_index(sn); 
        try: pv=int(pp.get('pada','0'))
        except: pv=0
        ei,ep=pada(engv)
        padok=(ni==ei and pv==ep) if ni is not None else None
        if padok is False: per[pl]['fail']+=1
        if abs(off)>0.05:
            per[pl]['gt']+=1
            pos=engv%S; edge=round(min(pos-(ep-1)*PS, ep*PS-pos),4)
            out.append({
                'idx':idx,'date':rec['date_of_birth'],'time':rec['time_of_birth'],
                'planet':pl,'engine_deg':round(engv,4),'ics_deg':round(true_ics,4),
                'offset_deg':round(off,4),'engine_nak_pada':f"{NAK[ei]} p{ep}",
                'ics_star':sn,'ics_pada':pv,'pada_match':padok,
                'dist_to_pada_edge':edge,'corrupt_ref':corrupt,
                'ics_abs_field':round(abs_field,4) if abs_field is not None else None,
            })
out.sort(key=lambda r:(r['planet'],-abs(r['offset_deg'])))
payload={'meta':{'source':'engine vs ICS (tests/astrology_data .json)','loc':[LAT,LON,TZ],
    'threshold_deg':0.05,'total_flagged':len(out),
    'per_planet':{p:per[p] for p in PLANETS}},'cases':out}
open('venus_debug/all_planet_offsets_gt0.05.json','w') if False else None
import os; os.makedirs('debug_offsets',exist_ok=True)
path='debug_offsets/all_planet_offsets_gt0.05.json'
json.dump(payload,open(path,'w'),indent=2,ensure_ascii=False)
print("wrote",path)
print("\nper-planet:  n=compared  gt=|off|>0.05  fail=pada mismatch")
for p in PLANETS:
    print(f"  {p:<9} n={per[p]['n']:>4}  gt0.05={per[p]['gt']:>3}  padaFail={per[p]['fail']:>2}")
print(f"\ntotal flagged (>0.05): {len(out)}")
