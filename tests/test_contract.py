from pathlib import Path
import copy,hashlib,json,re
import pytest
from gltest.direct import create_address
ROOT=Path(__file__).parents[1]
META=json.loads((ROOT/'fixtures/source.json').read_bytes())
FILES={name:(ROOT/'fixtures'/name).read_bytes() for name in META['sources']}
SHA=lambda b:hashlib.sha256(b).hexdigest()

def build(vm,deploy):
 vm.warp('2026-10-21T00:00:00Z');c=deploy(str(ROOT/'contract.py'),sdk_version='v0.2.12')
 assert hasattr(c,'get_configuration'),'Public contract behavior not implemented'
 return c

def body(value):return (json.dumps(value,separators=(',',':'))+'\n').encode()
def serve(vm,name,data):vm.mock_web(re.escape(META['sources'][name]['test_url']),{'status':200,'body':data.decode('utf-8')})

def open_record(vm,c,program=None):
 data=FILES['program.json'] if program is None else body(program);serve(vm,'program.json',data)
 c.open_program('demo',META['sources']['program.json']['test_url'],SHA(data))
def get(c):return c.get_program('demo')
def source(events):return {'version':1,'events':events}
def event(i,s,e):return {'id':i,'start':s,'end':e}

def test_owner_cas_permissionless_derive_terminal_revoke_and_permanent_id(direct_vm,direct_deploy):
 c=build(direct_vm,direct_deploy);open_record(direct_vm,c);owner=get(c)['owner'];outsider=create_address('outsider')
 with direct_vm.prank(outsider):
  with direct_vm.expect_revert('owner'):c.confirm_program('demo',0,'b'*64)
  c.derive_program('demo',0)
  with direct_vm.expect_revert('owner'):c.revoke_program('demo',1,'withdraw')
 d=get(c);assert d['status']=='DERIVED' and d['revision']==1 and len(d['certificate_id'])==64
 with direct_vm.expect_revert('revision'):c.confirm_program('demo',0,d['certificate_id'])
 with direct_vm.expect_revert('certificate'):c.confirm_program('demo',1,'0'*64)
 c.confirm_program('demo',1,d['certificate_id']);assert get(c)['status']=='CONFIRMED' and get(c)['revision']==2
 with direct_vm.expect_revert():c.derive_program('demo',2)
 direct_vm.clear_mocks();c.revoke_program('demo',2,'Synthetic record withdrawn');d=get(c)
 assert d['owner']==owner and d['status']=='REVOKED' and d['revision']==3 and len(d['history'])==4
 with direct_vm.expect_revert():c.revoke_program('demo',3,'again')
 with direct_vm.expect_revert():open_record(direct_vm,c)

def test_independent_validator_refetches_bytes_and_rejects_complete_forged_packet(direct_vm,direct_deploy):
 c=build(direct_vm,direct_deploy);open_record(direct_vm,c);c.derive_program('demo',0);assert direct_vm.run_validator() is True
 packet=copy.deepcopy(get(c)['last_capture']);packet['binding']['record_id']='other';assert direct_vm.run_validator(leader_result=packet) is False
 packet=copy.deepcopy(get(c)['last_capture']);packet['result']['decision']='FABRICATED';assert direct_vm.run_validator(leader_result=packet) is False
 direct_vm.clear_mocks()
 for name,data in FILES.items():
  if name!='policy.json':serve(direct_vm,name,data+b' ')
 assert direct_vm.run_validator() is False

def test_failed_confirmation_source_unavailable_preserves_revision(direct_vm,direct_deploy):
 c=build(direct_vm,direct_deploy);open_record(direct_vm,c);c.derive_program('demo',0);d=get(c);direct_vm.clear_mocks()
 with direct_vm.expect_revert():c.confirm_program('demo',1,d['certificate_id'])
 assert get(c)==d

@pytest.mark.parametrize('repo',['.','..','%2e'])
def test_namespace_dot_repository_rejected_before_fetch(direct_vm,direct_deploy,repo):
 c=build(direct_vm,direct_deploy);url='https://raw.githubusercontent.com/example/'+repo+'/'+'a'*40+'/input.json'
 with direct_vm.expect_revert('commit-pinned'):c.open_program('bad',url,'b'*64)

def test_exact_fixture_metadata_and_zero_constructor_api(direct_vm,direct_deploy):
 for name,data in FILES.items():assert SHA(data)==META['sources'][name]['sha256'] and len(data)==META['sources'][name]['bytes'] and META['sources'][name]['public_url'] is None
 c=build(direct_vm,direct_deploy);assert c.get_configuration()['protocol']=='LaneLedger'+'-v1'

def test_source_duplicate_keys_nonfinite_hash_drift_and_response_bounds(direct_vm,direct_deploy):
 c=build(direct_vm,direct_deploy)
 for data in [b'{"version":1,"version":1}',b'{"version":NaN}',b'x',b'{}',b' '*16385]:
  direct_vm.clear_mocks();serve(direct_vm,'program.json',data)
  with direct_vm.expect_revert():c.open_program('bad',META['sources']['program.json']['test_url'],SHA(data))

def test_minimum_lanes_complete_assignments_and_earliest_overlap_witness(direct_vm,direct_deploy):
 c=build(direct_vm,direct_deploy);open_record(direct_vm,c);r=c.derive_program('demo',0)
 assert r['decision']=='SCHEDULED' and r['lane_count']==2 and r['lower_bound']=={'tick':1,'active_ids':['alpha','beta'],'count':2}
 assert [(x['id'],x['lane']) for x in r['assignments']]==[('alpha',0),('beta',1),('gamma',1),('delta',0),('epsilon',0)]
 assert r['lanes']==[['alpha','delta','epsilon'],['beta','gamma']]

def test_half_open_end_before_start_and_lowest_free_lane(direct_vm,direct_deploy):
 c=build(direct_vm,direct_deploy);open_record(direct_vm,c,source([event('b',0,2),event('A',0,2),event('d',2,3),event('c',2,4)]));r=c.derive_program('demo',0)
 assert [(x['id'],x['lane']) for x in r['assignments']]==[('A',0),('b',1),('d',0),('c',1)]
 assert r['lane_count']==2 and r['lower_bound']=={'tick':0,'active_ids':['A','b'],'count':2}

def test_nested_intervals_have_exact_matching_lower_bound(direct_vm,direct_deploy):
 c=build(direct_vm,direct_deploy);open_record(direct_vm,c,source([event('outer',0,10),event('mid',1,9),event('inner',2,8)]));r=c.derive_program('demo',0)
 assert r['lane_count']==3 and r['lower_bound']=={'tick':2,'active_ids':['inner','mid','outer'],'count':3}

def test_empty_program_explicit_zero_lane_state(direct_vm,direct_deploy):
 c=build(direct_vm,direct_deploy);open_record(direct_vm,c,source([]));r=c.derive_program('demo',0)
 assert r=={'decision':'EMPTY','assignments':[],'lanes':[],'lane_count':0,'lower_bound':{'tick':None,'active_ids':[],'count':0}}

@pytest.mark.parametrize('change',['bool','float','negative','zero','reverse','duplicate','unknown','oversize','version_bool','bad_id','nonfinite'])
def test_strict_interval_and_size_boundaries(direct_vm,direct_deploy,change):
 s=source([event('a',0,2)])
 if change=='bool':s['events'][0]['start']=False
 if change=='float':s['events'][0]['end']=2.0
 if change=='negative':s['events'][0]['start']=-1
 if change=='zero':s['events'][0]['end']=0
 if change=='reverse':s['events'][0]['start']=3
 if change=='duplicate':s['events'].append(event('a',3,4))
 if change=='unknown':s['events'][0]['extra']=1
 if change=='oversize':s['events']=[event('r'+str(i),0,1) for i in range(17)]
 if change=='version_bool':s['version']=True
 if change=='bad_id':s['events'][0]['id']='bad id'
 if change=='nonfinite':s['events'][0]['end']=float('nan')
 c=build(direct_vm,direct_deploy)
 with direct_vm.expect_revert():open_record(direct_vm,c,s)

def test_sixteen_simultaneous_intervals_resource_boundary(direct_vm,direct_deploy):
 c=build(direct_vm,direct_deploy);open_record(direct_vm,c,source([event('r'+str(i).zfill(2),0,1000000) for i in range(16)]));r=c.derive_program('demo',0)
 assert r['lane_count']==16 and r['lower_bound']['count']==16 and r['lower_bound']['tick']==0

def test_validator_rejects_feasible_minimum_but_noncanonical_lane_relabeling(direct_vm,direct_deploy):
 c=build(direct_vm,direct_deploy);open_record(direct_vm,c);c.derive_program('demo',0)
 packet=copy.deepcopy(get(c)['last_capture']);r=packet['result'];r['lanes']=list(reversed(r['lanes']))
 for assignment in r['assignments']:assignment['lane']=1-assignment['lane']
 assert r['lane_count']==r['lower_bound']['count']==2
 assert direct_vm.run_validator(leader_result=packet) is False
