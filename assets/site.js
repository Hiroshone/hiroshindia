const menu=document.querySelector('.menu-toggle');
menu?.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));document.querySelector('#navigation').classList.toggle('open',open)});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&menu?.getAttribute('aria-expanded')==='true'){menu.click();menu.focus()}});
const quote=document.querySelector('#quote-form');
const partner=document.querySelector('#partner-form');
const review=document.querySelector('#review');
const names={odc_length:'Length (metres)',odc_width:'Width (metres)',odc_height:'Height (metres)',odc_weight:'Total weight (tonnes)',odc_handling:'Loading and unloading facilities',name:'Name',phone:'Phone / WhatsApp',email:'Email',company:'Business / organisation',origin:'Pickup / service location',destination:'Delivery location',date:'Preferred date',pincodes:'PIN codes',weight:'Approximate weight',packages:'Packages',dimensions:'Dimensions',vehicle_model:'Vehicle',truck_type:'Truck requirement',temperature:'Temperature requirement',access:'Site / packing details',vessel:'Vessel / port details',details:'Requirement',location:'City / state',pincode:'PIN code',role:'Partnership interest',coverage:'Areas / routes I can support',support:'Where I need HIROSH support',capabilities:'Capabilities and experience',volume:'Freight / other details'};
function invalidate(){if(review)review.hidden=true}
if(quote){
 const select=document.querySelector('#service');
 const initial=new URLSearchParams(location.search).get('service');
 if([...select.options].some(o=>o.value===initial))select.value=initial;
 function serviceFields(){
  const s=select.value;
  const vehicle=['car-transport','bike-transport','vehicle-storage'].includes(s);
  const maritime=s==='maritime-shipping';
  const relocation=['household-furniture','office-relocation','packing-handling'].includes(s);
  const enabled={cargo:!vehicle&&!maritime&&s!=='odc-cargo-transport',odc:s==='odc-cargo-transport',vehicle,maritime,relocation,truck:['truck-trailer-rental','trailer-transport','full-truck-load'].includes(s),reefer:s==='reefer-transport'};
  for(const section of document.querySelectorAll('[data-fields]')){const show=enabled[section.dataset.fields];section.hidden=!show;section.querySelectorAll('input,select,textarea').forEach(i=>i.disabled=!show)}
  document.querySelector('#origin-label').textContent=maritime?'Port / service location *':s==='vehicle-storage'?'Storage location *':'Pickup city / location *';
  const dest=document.querySelector('#destination');dest.disabled=maritime||s==='vehicle-storage';dest.required=!dest.disabled;document.querySelector('#destination-wrap').hidden=dest.disabled;
  invalidate();
 }
 select.addEventListener('change',serviceFields);serviceFields();
}
function prepare(form,isPartner){
 form.addEventListener('input',invalidate);
 form.addEventListener('change',invalidate);
 form.addEventListener('submit',event=>{
  event.preventDefault();
  if(!form.reportValidity())return;
  const lines=[isPartner?'Hirosh Roadways Partnership Enquiry':'Hirosh Roadways Service Enquiry'];
  if(!isPartner)lines.push('Service: '+document.querySelector('#service').selectedOptions[0].textContent);
  for(const [key,value] of new FormData(form)){if(key==='consent'||key==='service'||!String(value).trim())continue;lines.push((names[key]||key)+': '+String(value).trim())}
  const message=lines.join('\n');
  document.querySelector('#review-text').textContent=message;
  document.querySelector('#send-whatsapp').href='https://wa.me/'+(isPartner?'919446937639':'919446937638')+'?text='+encodeURIComponent(message);
  document.querySelector('#send-email').href='mailto:'+(isPartner?'info@hiroshindia.com':'sales@hiroshindia.com')+'?subject='+encodeURIComponent(lines[0])+'&body='+encodeURIComponent(message);
  review.hidden=false;review.focus();review.scrollIntoView({block:'nearest',behavior:'auto'});
 });
}
if(quote)prepare(quote,false);
if(partner)prepare(partner,true);
