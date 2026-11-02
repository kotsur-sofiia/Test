/* Long-press sorting: let early touch movement scroll; persist once on drop. */
'use strict';
window.WomanTopicReorder=Object.freeze({attach({list,dialog,onDrop,announce}){
  let session=null,frame=null,suppressClickUntil=0;
  const handle=row=>row?.querySelector('[data-action=reorder]');
  const enabled=()=>[...list.querySelectorAll('.topic-editor-row.is-enabled')];
  function cleanup(restore){
    const s=session;if(!s)return null;session=null;clearTimeout(s.timer);cancelAnimationFrame(frame);frame=null;
    s.ghost?.remove();s.row.classList.remove('drag-placeholder','keyboard-grabbed');handle(s.row)?.setAttribute('aria-pressed','false');
    if(restore)for(const node of s.originalNodes)if(node.parentElement===list)list.append(node);
    return s;
  }
  function cancel(){const s=cleanup(true);if(s?.active)announce('Перемещение отменено.');}
  function preview(y){
    const s=session;if(!s?.active||s.keyboard)return;
    const others=enabled().filter(row=>row!==s.row);
    const before=others.find(row=>{const b=row.getBoundingClientRect();return y<b.top+b.height/2;});
    const target=before||list.querySelector('.topic-editor-row:not(.is-enabled)');if(s.row.nextSibling!==target)list.insertBefore(s.row,target);
    const position=enabled().indexOf(s.row);
    if(s.position!==position){s.position=position;announce('«'+s.name+'»: позиция '+(position+1)+'.');}
  }
  function tick(){
    const s=session;if(!s?.active||s.keyboard)return;
    const bounds=dialog.getBoundingClientRect(),header=dialog.querySelector('.sheet-heading').getBoundingClientRect();
    const top=Math.max(bounds.top,header.bottom)+8,bottom=bounds.bottom-18;
    if(s.y<top+40)dialog.scrollTop-=Math.min(14,(top+40-s.y)/3);
    else if(s.y>bottom-40)dialog.scrollTop+=Math.min(14,(s.y-bottom+40)/3);
    s.ghost.style.top=(s.y-s.offsetY)+'px';preview(s.y);frame=requestAnimationFrame(tick);
  }
  function activate(){
    const s=session;if(!s||!dialog.open||!s.row.isConnected)return cancel();
    s.active=true;handle(s.row)?.setAttribute('aria-pressed','true');
    if(s.keyboard)s.row.classList.add('keyboard-grabbed');
    else {
      const box=s.row.getBoundingClientRect();s.offsetY=Math.max(0,Math.min(box.height,s.y-box.top));
      const ghost=s.row.cloneNode(true);ghost.removeAttribute('data-topic');ghost.classList.add('topic-drag-ghost');ghost.setAttribute('aria-hidden','true');ghost.inert=true;
      Object.assign(ghost.style,{left:box.left+'px',top:box.top+'px',width:box.width+'px'});dialog.append(ghost);s.ghost=ghost;s.row.classList.add('drag-placeholder');tick();
    }
    announce('Тема «'+s.name+'» выбрана для перемещения.');
  }
  function begin(row,x,y,id,keyboard=false){
    if(session)cancel();
    session={row,id,x,y,startX:x,startY:y,keyboard,active:false,originalNodes:[...list.children],name:row.querySelector('strong').textContent};
    if(keyboard)activate();else session.timer=setTimeout(activate,400);
  }
  function move(x,y,event){
    const s=session;if(!s)return;
    if(!s.active){if(Math.hypot(x-s.startX,y-s.startY)>9)cancel();return;}
    if(event.cancelable)event.preventDefault();s.x=x;s.y=y;preview(y);
  }
  function finish(){
    const order=enabled().map(row=>row.dataset.topic),s=cleanup(false);if(!s?.active)return;
    suppressClickUntil=performance.now()+350;onDrop(order,s.row.dataset.topic);
  }
  function dragRow(target){
    if(target.closest('[data-action=toggle],input,select,textarea'))return null;
    return target.closest('.topic-editor-row.is-enabled');
  }
  list.addEventListener('touchstart',event=>{
    if(event.touches.length!==1)return cancel();const row=dragRow(event.target);if(!row)return;
    const t=event.touches[0];begin(row,t.clientX,t.clientY,t.identifier);
  },{passive:true});
  list.addEventListener('touchmove',event=>{
    if(!session||session.keyboard)return;const t=[...event.touches].find(t=>t.identifier===session.id);if(t)move(t.clientX,t.clientY,event);
  },{passive:false});
  list.addEventListener('touchend',event=>{
    if(!session||session.keyboard)return;
    if([...event.changedTouches].some(t=>t.identifier===session.id)){if(session.active&&event.cancelable)event.preventDefault();finish();}
  },{passive:false});
  list.addEventListener('touchcancel',cancel);
  list.addEventListener('pointerdown',event=>{
    suppressClickUntil=0;
    if(event.pointerType==='touch'||event.button!==0)return;
    const row=dragRow(event.target);if(row)begin(row,event.clientX,event.clientY,'pointer-'+event.pointerId);
  });
  document.addEventListener('pointermove',event=>{if(session?.id==='pointer-'+event.pointerId)move(event.clientX,event.clientY,event);},{passive:false});
  document.addEventListener('pointerup',event=>{if(session?.id==='pointer-'+event.pointerId)finish();});
  document.addEventListener('pointercancel',event=>{if(session?.id==='pointer-'+event.pointerId)cancel();});
  list.addEventListener('click',event=>{if(performance.now()<suppressClickUntil){event.preventDefault();event.stopImmediatePropagation();}},{capture:true});
  list.addEventListener('contextmenu',event=>{if(event.target.closest('.is-enabled'))event.preventDefault();});
  list.addEventListener('keydown',event=>{
    if(event.key==='Tab'&&session?.keyboard)cancel();
    const control=event.target.closest('[data-action=reorder]');if(!control)return;
    const row=control.closest('.topic-editor-row');
    if([' ','Enter'].includes(event.key)){
      event.preventDefault();if(session?.active&&session.keyboard)finish();else begin(row,0,0,'keyboard',true);
    } else if(session?.keyboard&&event.key==='Escape'){
      event.preventDefault();event.stopPropagation();cancel();control.focus({preventScroll:true});
    } else if(session?.keyboard&&['ArrowUp','ArrowDown'].includes(event.key)){
      event.preventDefault();const rows=enabled(),index=rows.indexOf(row),delta=event.key==='ArrowUp'?-1:1,target=rows[index+delta];
      if(target){if(delta<0)list.insertBefore(row,target);else list.insertBefore(row,target.nextSibling);control.focus({preventScroll:true});row.scrollIntoView({block:'nearest'});announce('«'+session.name+'»: позиция '+(index+delta+1)+'.');}
    }
  });
  dialog.addEventListener('close',cancel);
  dialog.addEventListener('cancel',event=>{if(session?.active){event.preventDefault();cancel();}});
  window.addEventListener('resize',cancel);window.addEventListener('blur',cancel);
  document.addEventListener('visibilitychange',()=>{if(document.hidden)cancel();});
  return Object.freeze({cancel});
}});
