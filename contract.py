# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import hashlib,json,re
from datetime import datetime,timezone

def _require(ok: bool,message: str) -> None:
 if not ok:raise gl.vm.UserError('[EXPECTED] '+message)
def _canonical(value) -> str:return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)
def _now() -> int:
 value=datetime.fromisoformat(gl.message_raw['datetime'].replace('Z','+00:00'))
 if value.tzinfo is None:value=value.replace(tzinfo=timezone.utc)
 delta=value.astimezone(timezone.utc)-datetime(1970,1,1,tzinfo=timezone.utc)
 return delta.days*86400+delta.seconds
def _identifier(value) -> None:_require(isinstance(value,str) and re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,23}',value) is not None,'invalid ASCII identifier')
def _integer(value,lo: int,hi: int) -> bool:return type(value) is int and lo<=value<=hi
def _source(url: str,digest: str) -> None:
 pattern=r'https://raw\.githubusercontent\.com/[A-Za-z0-9-]{1,39}/[A-Za-z0-9_.-]{1,100}/[0-9a-f]{40}/[A-Za-z0-9_.~/-]+'
 _require(isinstance(url,str) and len(url)<=512 and re.fullmatch(pattern,url) is not None and all(part not in ('','.','..') for part in url.split('/')[3:]),'canonical commit-pinned URL required')
 _require(isinstance(digest,str) and re.fullmatch(r'[0-9a-f]{64}',digest) is not None,'invalid SHA256')
def _unique(pairs: list) -> dict:
 out={}
 for key,value in pairs:
  _require(key not in out,'duplicate JSON key');out[key]=value
 return out
def _constant(value):raise gl.vm.UserError('[SOURCE] nonfinite JSON constant')
def _parse(body: bytes):
 _require(1<=len(body)<=16384,'source byte bound')
 try:return json.loads(body.decode('utf-8'),object_pairs_hook=_unique,parse_constant=_constant)
 except (ValueError,UnicodeError,RecursionError):raise gl.vm.UserError('[SOURCE] invalid UTF8 JSON')
def _fetch(url: str,digest: str) -> dict:
 response=gl.nondet.web.get(url,headers={'Accept':'application/json'})
 _require(response.status==200 and response.body is not None and 1<=len(response.body)<=16384,'SOURCE unavailable or oversized')
 _require(hashlib.sha256(response.body).hexdigest()==digest,'SOURCE byte SHA256 mismatch')
 return _validate(_parse(response.body))

def _validate(value) -> dict:
 _require(isinstance(value,dict) and set(value)=={'version','events'} and type(value['version']) is int and value['version']==1,'source schema')
 events=value['events'];_require(isinstance(events,list) and len(events)<=16,'0..16 events required');seen=set()
 for event in events:
  _require(isinstance(event,dict) and set(event)=={'id','start','end'},'event fields');_identifier(event['id'])
  _require(event['id'] not in seen,'duplicate event ID');seen.add(event['id'])
  _require(_integer(event['start'],0,1000000) and _integer(event['end'],0,1000000) and event['start']<event['end'],'strict half-open integer interval')
 return {'version':1,'events':sorted(events,key=lambda x:(x['start'],x['end'],x['id']))}
def _derive(sources: list,policy: dict) -> dict:
 events=sources[0]['events'];ends=[];lanes=[];assignments=[]
 for event in events:
  lane=next((i for i,end in enumerate(ends) if end<=event['start']),len(ends))
  if lane==len(ends):ends.append(event['end']);lanes.append([])
  else:ends[lane]=event['end']
  lanes[lane].append(event['id']);assignments.append({'id':event['id'],'start':event['start'],'end':event['end'],'lane':lane})
 # Independent lower-bound scan uses input intervals, never the lane assignments.
 bound={'tick':None,'active_ids':[],'count':0}
 ticks=sorted(set(t for event in events for t in (event['start'],event['end'])))
 for tick in ticks:
  active=sorted(event['id'] for event in events if event['start']<=tick<event['end'])
  if len(active)>bound['count']:bound={'tick':tick,'active_ids':active,'count':len(active)}
 _require(len(lanes)==bound['count'],'minimum-lane lower-bound invariant')
 return {'decision':'SCHEDULED' if events else 'EMPTY','assignments':assignments,'lanes':lanes,'lane_count':len(lanes),'lower_bound':bound}

def _capture(locators: list,policy: dict,binding: dict) -> dict:
 def leader() -> dict:
  sources=[_fetch(locator['url'],locator['sha256']) for locator in locators]
  return {'binding':binding,'sources':sources,'result':None if binding['operation']=='open' else _derive(sources,policy)}
 def validator(proposed: gl.vm.Result) -> bool:
  if not isinstance(proposed,gl.vm.Return):return False
  try:return _canonical(leader())==_canonical(proposed.calldata)
  except Exception:return False
 return gl.vm.run_nondet_unsafe(leader,validator)

class LaneLedger(gl.Contract):
 records: TreeMap[str,str]
 def __init__(self):pass
 def _get(self,record_id: str) -> dict:
  _identifier(record_id);_require(record_id in self.records,'unknown record');return json.loads(self.records[record_id])
 def _revision(self,r: dict,revision: int) -> None:_require(type(revision) is int and revision==r['revision'],'stale revision')
 def _owner(self,r: dict) -> None:_require(gl.message.sender_address.as_hex.lower()==r['owner'],'owner only')
 def _binding(self,r: dict,operation: str) -> dict:
  return {'protocol':'LaneLedger-v1','chain_id':int(gl.message.chain_id),'contract':gl.message.contract_address.as_hex.lower(),'owner':r['owner'],'record_id':r['record_id'],'locators':r['locators'],'policy':r['policy'],'revision':r['revision'],'operation':operation,'observed_at':_now()}
 def _history(self,r: dict) -> None:
  _require(len(r['history'])<4,'finite history bound');r['history'].append({'status':r['status'],'revision':r['revision'],'at':_now(),'certificate_id':r['certificate_id']})
 def _open(self,record_id: str,locators: list,policy: dict) -> None:
  _identifier(record_id);_require(record_id not in self.records,'record ID already used')
  r={'record_id':record_id,'owner':gl.message.sender_address.as_hex.lower(),'locators':locators,'policy':policy,'status':'OPEN','revision':0,'certificate_id':'','reason':'','sources':[],'result':None,'last_capture':None,'history':[]}
  packet=_capture(locators,policy,self._binding(r,'open'));r['sources']=packet['sources'];r['last_capture']=packet;self._history(r);self.records[record_id]=_canonical(r)
 @gl.public.write
 def open_program(self,record_id: str,source_url: str,source_sha256: str) -> None:
  _source(source_url,source_sha256);self._open(record_id,[{'url':source_url,'sha256':source_sha256}],{})

 @gl.public.write
 def derive_program(self,record_id: str,expected_revision: int) -> dict:
  r=self._get(record_id);self._revision(r,expected_revision);_require(r['status']=='OPEN','record not OPEN')
  packet=_capture(r['locators'],r['policy'],self._binding(r,'derive'));_require(_canonical(packet['sources'])==_canonical(r['sources']),'source snapshot mismatch')
  r['result']=packet['result'];r['last_capture']=packet;r['certificate_id']=hashlib.sha256(_canonical(packet).encode('utf-8')).hexdigest();r['status']='DERIVED';r['revision']=1;self._history(r);self.records[record_id]=_canonical(r);return r['result']
 @gl.public.write
 def confirm_program(self,record_id: str,expected_revision: int,certificate_id: str) -> None:
  r=self._get(record_id);self._owner(r);self._revision(r,expected_revision);_require(r['status']=='DERIVED','record not DERIVED');_require(isinstance(certificate_id,str) and certificate_id==r['certificate_id'],'current certificate required')
  packet=_capture(r['locators'],r['policy'],self._binding(r,'confirm'));_require(_canonical(packet['sources'])==_canonical(r['sources']) and _canonical(packet['result'])==_canonical(r['result']),'fresh complete result mismatch')
  r['last_capture']=packet;r['status']='CONFIRMED';r['revision']=2;self._history(r);self.records[record_id]=_canonical(r)
 @gl.public.write
 def revoke_program(self,record_id: str,expected_revision: int,reason: str) -> None:
  r=self._get(record_id);self._owner(r);self._revision(r,expected_revision);_require(r['status']!='REVOKED','record already revoked');_require(isinstance(reason,str) and reason==reason.strip() and 1<=len(reason)<=160,'reason1..160 trimmed')
  r['status']='REVOKED';r['revision']+=1;r['reason']=reason;self._history(r);self.records[record_id]=_canonical(r)
 @gl.public.view
 def get_program(self,record_id: str) -> dict:return self._get(record_id)
 @gl.public.view
 def get_configuration(self) -> dict:return {'protocol':'LaneLedger-v1','max_events':16,'max_tick':1000000,'max_source_bytes':16384,'actual_booking_performed':False}
