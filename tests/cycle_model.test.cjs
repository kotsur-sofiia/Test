const assert=require('node:assert/strict');
const {snapshot,advice}=require('../cycle-model.js');
const base={periods:['2026-10-13'],length:28,periodLength:5,predict:true};
const get=date=>snapshot({...base,date});
assert.equal(get('2026-10-13').day,1);assert.equal(get('2026-10-13').progress,0);
assert.equal(get('2026-11-02').day,21);assert.equal(get('2026-11-02').phase,'luteal');
assert.equal(get('2026-11-02').remaining,8); // Nov 2 -> expected Nov 10; count actual calendar days.
assert.equal(get('2026-11-09').remaining,1);
assert.equal(get('2026-11-10').status,'awaiting');assert.equal(get('2026-11-10').day,29);
assert.equal(get('2026-11-11').overdue,1);assert.equal(get('2026-11-11').phase,null);
assert.equal(get('2026-11-11').displayPhase,'luteal');
assert.equal(get('2026-11-30').displayPhase,'luteal');
assert.equal(get('2026-11-30').day,49);assert.equal(get('2026-11-30').overdue,20);
assert.equal(snapshot({...base,date:'2026-11-11',predict:false}).displayPhase,undefined);
assert.equal(snapshot({...base,date:'2026-11-11',periods:[...base.periods,'2026-11-10']}).phase,'menstrual');
assert.equal(get('2026-10-12').day,null);assert.equal(get('2026-02-30').status,'empty');
assert.equal(snapshot({...base,date:'2026-11-02',predict:false}).phase,null);
assert.equal(snapshot({...base,date:'2026-11-02',length:0}).status,'unavailable');
assert.equal(snapshot({...base,date:'2026-11-11',periods:[...base.periods,'2026-11-10']}).day,2);
assert.equal(snapshot({...base,date:'2024-03-01',periods:['2024-02-28']}).day,3);
assert.equal(snapshot({...base,date:'2026-10-26',periods:['2026-10-24']}).day,3); // DST end.
assert.notDeepEqual(advice(get('2026-10-29')),advice(get('2026-11-05')));
assert.equal(advice(get('2026-11-11')).tips.length,3);
console.log('PASS: cycle clock starts at day one, actual date countdown, no automatic reset, restrictions, invalid dates, leap/DST days and date-specific care');
