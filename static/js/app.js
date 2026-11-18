let donutChart = null;
let latencyChart = null;
const el = id => document.getElementById(id);

function payload() {
  return {
    addresses: el("addresses").value,
    block_size: Number(el("blockSize").value),
    mapping: el("mapping").value,
    associativity: Number(el("associativity").value),
    replacement: el("replacement").value,
    memory_penalty: Number(el("memoryPenalty").value),
    levels: [
      {name:"L1 Cache",size_kb:Number(el("l1Size").value),access_time:Number(el("l1Time").value),enabled:el("enableL1").checked},
      {name:"L2 Cache",size_kb:Number(el("l2Size").value),access_time:Number(el("l2Time").value),enabled:el("enableL2").checked},
      {name:"L3 Cache",size_kb:Number(el("l3Size").value),access_time:Number(el("l3Time").value),enabled:el("enableL3").checked}
    ]
  };
}
async function post(url, data) {
  const response = await fetch(url,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});
  const body = await response.json();
  if (!response.ok || !body.success) throw new Error(body.error || "Request failed.");
  return body.result;
}
function error(message) {
  const box=el("error"); box.textContent=message; box.style.display=message?"block":"none";
}
function render(result) {
  const s=result.summary;
  el("total").textContent=s.total_accesses;
  el("hit").textContent=s.hit_ratio+"%";
  el("miss").textContent=s.miss_ratio+"%";
  el("amat").textContent=s.amat+" ns";
  el("runStatus").textContent="SIMULATION COMPLETE";
  el("empty1").style.display="none"; el("empty2").style.display="none";
  if(donutChart)donutChart.destroy();
  donutChart=new Chart(el("distribution"),{
    type:"doughnut",
    data:{labels:["Cache hit","Main memory access"],datasets:[{data:[s.memory_hits,s.memory_misses],backgroundColor:["#55d5a4","#ffb16b"],borderColor:"#111a29",borderWidth:4}]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:"bottom",labels:{color:"#aab8ca",font:{family:"Manrope",size:10}}}}}
  });
  if(latencyChart)latencyChart.destroy();
  latencyChart=new Chart(el("latency"),{
    type:"line",
    data:{labels:result.trace.map(x=>"Step "+x.step),datasets:[{label:"Latency (ns)",data:result.trace.map(x=>x.latency),borderColor:"#63b8ff",backgroundColor:"#63b8ff20",fill:true,tension:.3,pointRadius:3}]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{ticks:{color:"#8293aa"},grid:{color:"#263247"}},y:{beginAtZero:true,ticks:{color:"#8293aa"},grid:{color:"#263247"}}}}
  });
  el("levelRows").innerHTML=result.levels.map(x=>`<tr><td><b>${x.name}</b></td><td>${x.capacity_kb} KB</td><td>${x.hits}</td><td>${x.misses}</td><td>${x.evictions}</td><td>${x.hit_ratio}%</td><td>${x.lines.length}</td></tr>`).join("");
  el("traceRows").innerHTML=result.trace.map(x=>{
    const hit=x.found_at!=="Main Memory";
    const lookup=x.levels.map(y=>`${y.level}: ${y.hit?"HIT":"MISS"}`).join(" → ");
    return `<tr><td>${x.step}</td><td>${x.hex} (${x.address})</td><td><span class="${hit?"hit-pill":"miss-pill"}">${hit?"CACHE HIT":"MEMORY MISS"}</span></td><td>${x.found_at}</td><td>${x.latency} ns</td><td>${lookup}</td></tr>`;
  }).join("");
}
async function runSimulation(){
  error(""); const btn=el("runBtn");btn.disabled=true;btn.textContent="Running...";
  try{const result=await post("/api/simulate",payload());render(result);}
  catch(e){error(e.message);}
  finally{btn.disabled=false;btn.textContent="▶  Run simulation";}
}
async function compare(){
  error("");const btn=el("compareBtn");btn.disabled=true;btn.textContent="Comparing...";
  try{const rows=await post("/api/compare",payload());el("compareRows").innerHTML=rows.map(x=>`<tr><td><b>${x.algorithm}</b></td><td>${x.hit_ratio}%</td><td>${x.miss_ratio}%</td><td>${x.amat} ns</td><td>${x.main_memory_accesses}</td></tr>`).join("");}
  catch(e){error(e.message);}
  finally{btn.disabled=false;btn.textContent="⇄  Compare replacement algorithms";}
}
el("runBtn").addEventListener("click",runSimulation);
el("compareBtn").addEventListener("click",compare);
el("mapping").addEventListener("change",()=>{el("associativity").disabled=el("mapping").value!=="set_associative";});
el("associativity").disabled=el("mapping").value!=="set_associative";
