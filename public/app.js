let events=[], view=new Date(), filter="All";
const $=s=>document.querySelector(s);
function pad(n){return String(n).padStart(2,"0")}
function key(d){return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`}
function fmtDate(s){return new Date(s+"T12:00:00").toLocaleDateString("en-US",{weekday:"short",month:"short",day:"numeric"})}
function visible(){return events.filter(e=>filter==="All"||e.category===filter)}
function render(){
  $("#month").textContent=view.toLocaleDateString("en-US",{month:"long",year:"numeric"});
  const y=view.getFullYear(),m=view.getMonth(),first=new Date(y,m,1),last=new Date(y,m+1,0);
  let start=(first.getDay()+6)%7, html="";
  for(let i=0;i<start;i++)html+='<div class="day other"></div>';
  for(let d=1;d<=last.getDate();d++){
    const k=`${y}-${pad(m+1)}-${pad(d)}`, es=visible().filter(e=>e.date===k);
    html+=`<div class="day"><div class="daynum">${d}</div>${es.map(e=>`<button class="event-pill" data-id="${e.id}">${escapeHtml(e.title)}</button>`).join("")}</div>`;
  }
  $("#days").innerHTML=html;
  const upcoming=visible().filter(e=>e.date>=key(new Date())).sort((a,b)=>a.date.localeCompare(b.date));
  $("#count").textContent=`${upcoming.length} event${upcoming.length===1?"":"s"}`;
  $("#events").innerHTML=upcoming.length?upcoming.map(card).join(""):'<p style="color:var(--muted)">No upcoming events match this filter.</p>';
  document.querySelectorAll(".event-pill").forEach(b=>b.onclick=()=>{const e=events.find(x=>x.id===b.dataset.id);if(e)document.getElementById(e.id)?.scrollIntoView({behavior:"smooth"})});
}
function card(e){return `<article class="event-card" id="${e.id}"><div class="event-top"><div><h3 class="event-title">${escapeHtml(e.title)}</h3><div class="meta">${escapeHtml(e.time)} · ${escapeHtml(e.venue)}, ${escapeHtml(e.city)}</div></div><div class="date">${fmtDate(e.date)}</div></div><div class="tags"><span class="tag">${escapeHtml(e.category)}</span></div><div class="meta">${escapeHtml(e.description||"")}</div><div class="source">Source: <a href="${e.url}" target="_blank" rel="noopener">${escapeHtml(e.source)}</a></div></article>`}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]))}
$("#prev").onclick=()=>{view=new Date(view.getFullYear(),view.getMonth()-1,1);render()}
$("#next").onclick=()=>{view=new Date(view.getFullYear(),view.getMonth()+1,1);render()}
$("#today").onclick=()=>{view=new Date();render()}
document.querySelectorAll("[data-filter]").forEach(b=>b.onclick=()=>{filter=b.dataset.filter;document.querySelectorAll("[data-filter]").forEach(x=>x.classList.toggle("active",x===b));render()})
fetch("events.json").then(r=>r.json()).then(data=>{events=Array.isArray(data)?data:[];render()}).catch(()=>{$("#events").innerHTML='<p style="color:var(--muted)">Could not load the event feed.</p>'});
