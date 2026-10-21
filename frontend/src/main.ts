import './style.css';
import fixture from '../../fixtures/program.json';
import meta from '../../fixtures/source.json';
import {validateSource,derive,inspectAt,checkResult,type Source,type Result} from './domain';
import {boot,el,value,cell,json,exportJSON} from './shell';
import {lockArgs} from './wallet';
import {parsePublicJSON} from './public-json';
const workspace='<section class="card"><p class="eyebrow">MINIMUM SIMULTANEOUS LANES</p><h2>See why this many lanes are necessary</h2><span id="viewMode" class="tag">Local synthetic preview</span><p>Intervals use [start,end): ending releases a lane before another event starts. The lowest free lane is reused. Maximum simultaneous overlap is an independent lower bound.</p><div id="score" class="score"></div><svg id="timeline" viewBox="0 0 720 180" role="img" aria-label="Canonical minimum lane timeline with inspection tick"></svg><label>Inspect abstract tick <output id="instantLabel"></output><input id="instant" type="range" min="0" step="1" value="1"></label><p id="active" role="status"></p><p id="bound"></p><button id="jumpBound" class="secondary">Inspect earliest maximum overlap</button><h3>Canonical event assignment</h3><div id="events" class="table-wrap"></div><details><summary>Full result and overlap witness</summary><pre id="result"></pre></details></section><section class="card"><h2>Edit a fictional program</h2><p class="small">0..16 unique events, integer ticks0..1000000 and start &lt; end. Ticks have no real time zone, attendance, reservation or external execution meaning.</p><label>Program JSON<textarea id="programJson" spellcheck="false"></textarea></label><div class="pair"><button id="applyPreview" class="secondary">Validate local program</button><button id="exportProgram" class="secondary">Export exact JSON bytes</button></div><pre id="exportInfo"></pre></section>';
const fields='<label>Published program commit URL<input id="sourceUrl" placeholder="Publish program.json first"></label><label>Exact source-byte SHA256<input id="sourceSha" value="'+meta.sources['program.json'].sha256+'"></label><p class="small">Opening reads the public URL, not the local editor. Export and publish changed data first.</p>';
const app=boot('LaneLedger','program','An exact interval partition and its matching overlap lower bound. Inspect canonical lanes on declared synthetic ticks; no real booking or work execution occurs.',workspace,fields,()=>lockArgs(value('recordId'),value('sourceUrl'),value('sourceSha')));
let program:Source=validateSource(fixture),result:Result=derive([program],{}),mode='Local synthetic preview';
const colors=['#277d89','#675e9b','#b86e4c','#4878b0','#6c8a48','#a65375'];
function svg(tag:string,attrs:Record<string,string>){const n=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v]of Object.entries(attrs))n.setAttribute(k,v);return n;}
function render(){
 result=derive([program],{});el('viewMode').textContent=mode;const slider=el<HTMLInputElement>('instant'),maximum=Math.max(1,...program.events.map(e=>e.end));slider.max=String(maximum);if(Number(slider.value)>maximum||!Number.isInteger(Number(slider.value)))slider.value='0';const tick=Number(slider.value),active=inspectAt(program,tick);
 el('instantLabel').textContent=String(tick);el('active').textContent='At tick '+tick+': '+active.length+' active · '+(active.join(', ')||'none')+'. Endpoints are half-open.';
 el('bound').textContent=result.lower_bound.tick===null?'EMPTY: zero events, zero lanes, no overlap witness.':'Earliest maximum overlap: tick '+result.lower_bound.tick+', '+result.lower_bound.count+' events ['+result.lower_bound.active_ids.join(', ')+']. This proves at least '+result.lower_bound.count+' lanes; the assignment uses exactly '+result.lane_count+'.';
 el('score').replaceChildren();for(const [label,text]of [['Decision',result.decision],['Minimum lanes',String(result.lane_count)],['Events',String(program.events.length)],['Lower bound',String(result.lower_bound.count)]]){const box=document.createElement('div');cell(box,label,'small');cell(box,text,'strong');el('score').append(box);}
 const timeline=el('timeline'),height=Math.max(90,65+result.lane_count*42),x=(t:number)=>80+t/maximum*610;timeline.replaceChildren();timeline.setAttribute('viewBox','0 0 720 '+height);
 for(let lane=0;lane<result.lane_count;lane++){const label=svg('text',{x:'10',y:String(38+lane*42),class:'lane-label'});label.textContent='Lane '+lane;timeline.append(label);timeline.append(svg('line',{x1:'78',y1:String(46+lane*42),x2:'695',y2:String(46+lane*42),stroke:'#dce5ed'}));}
 for(const e of result.assignments){timeline.append(svg('rect',{x:String(x(e.start)),y:String(20+e.lane*42),width:String(Math.max(.5,x(e.end)-x(e.start))),height:'26',rx:'4',fill:colors[e.lane%colors.length]}));const label=svg('text',{x:String(x(e.start)+5),y:String(37+e.lane*42),class:'event-label'});label.textContent=e.id+' ['+e.start+','+e.end+')';timeline.append(label);}
 timeline.append(svg('line',{x1:String(x(tick)),x2:String(x(tick)),y1:'7',y2:String(height-20),class:'tick-line'}));
 const table=document.createElement('table'),head=document.createElement('tr');for(const text of ['ID','Start','End excluded','Lane','At inspected tick'])cell(head,text,'th');table.append(head);
 for(const e of result.assignments){const row=document.createElement('tr');for(const text of [e.id,String(e.start),String(e.end),String(e.lane),active.includes(e.id)?'ACTIVE':'—'])cell(row,text);table.append(row);}el('events').replaceChildren(table);el('result').textContent=json(result);
}
el('instant').addEventListener('input',render);
el('jumpBound').addEventListener('click',()=>{el<HTMLInputElement>('instant').value=String(result.lower_bound.tick??0);render();});
el('applyPreview').addEventListener('click',()=>app.run(async()=>{const next=validateSource(parsePublicJSON(el<HTMLTextAreaElement>('programJson').value));app.clear();program=next;mode='Edited local program · unpublished';el<HTMLTextAreaElement>('programJson').value=json(program);render();app.log('Program validated locally. Publish exact bytes separately before opening.');}));
el('exportProgram').addEventListener('click',()=>app.run(async()=>{el('exportInfo').textContent=await exportJSON('program.json',program);app.log('Exported public synthetic JSON only. No publication or chain write.');}));
app.hooks(record=>{
 if(!Array.isArray(record.sources)||record.sources.length!==1)throw Error('One complete program snapshot required.');
 const next=validateSource(record.sources[0]);if(record.result!==null)checkResult([next],{},record.result);program=next;
 mode=record.status==='REVOKED'?'Historical program · REVOKED':record.result===null?'Loaded source · local lane preview':'Verified loaded chain lane certificate';el<HTMLTextAreaElement>('programJson').value=json(program);render();
},()=>{mode='Local preview · no current chain context';el('viewMode').textContent=mode;});
el<HTMLTextAreaElement>('programJson').value=json(program);render();app.refresh();
