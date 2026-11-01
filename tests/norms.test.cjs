const assert=require('node:assert/strict');
require('../norms.js');
const p=(age,sex='female',status='none',ageUnit='years')=>({age,sex,status,ageUnit,weight:60,month:3});
const value=(key,profile)=>LunaDRI.get(key,profile)?.value??null;
// Selected independent DRI reference cases and boundary regressions.
assert.equal(value('potassium',p(35)),2600);
assert.equal(value('potassium',p(35,'male')),3400);
assert.equal(value('potassium',p(35,'female','pregnant')),2900);
assert.equal(value('potassium',p(16,'female','pregnant')),2600);
assert.equal(value('phosphorus',p(8)),500);
assert.equal(value('phosphorus',p(9)),1250);
assert.equal(value('phosphorus',p(18)),1250);
assert.equal(value('phosphorus',p(19)),700);
assert.equal(value('phosphorus',p(16,'female','pregnant')),1250);
assert.equal(value('phosphorus',p(35,'female','pregnant')),700);
assert.equal(value('calcium',p(50)),1000);
assert.equal(value('calcium',p(51)),1200);
assert.equal(value('calcium',p(51,'male')),1000);
assert.equal(value('calcium',p(71,'male')),1200);
assert.equal(value('magnesium',p(30,'female','pregnant')),350);
assert.equal(value('magnesium',p(31,'female','pregnant')),360);
assert.equal(value('magnesium',p(16,'female','pregnant')),400);
assert.equal(value('iron',p(35)),18);
assert.equal(value('iron',p(51)),8);
assert.equal(value('iron',p(35,'female','pregnant')),27);
assert.equal(value('folate',p(35,'female','planning')),400);
assert.equal(value('folate',p(35,'female','pregnant')),600);
assert.equal(value('sodium',p(2)),800);
assert.equal(value('sodium',p(7)),1000);
assert.equal(value('sodium',p(12)),1200);
assert.equal(value('sodium',p(35)),1500);
assert.equal(value('chloride',p(35)),2300);
assert.equal(value('d',p(70)),15);
assert.equal(value('d',p(71)),20);
assert.equal(value('potassium',p(6,'female','none','months')),400);
assert.equal(value('potassium',p(7,'female','none','months')),860);
assert.equal(value('fiber',p(7,'female','none','months')),null);
assert.equal(value('b3',p(3,'female','none','months')),null); // infant AI uses mg niacin, not NE
assert.equal(value('ala',p(7,'female','none','months')),null);
assert.equal(LunaDRI.get('iron',p(7,'female','none','months')).type,'RDA');
assert.equal(LunaDRI.get('calcium',p(7,'female','none','months')).type,'AI');
for(const profile of [null,p(0),p(-1),p(121),p(24,'female','none','months'),p(13,'female','pregnant'),p(51,'female','pregnant'),p(35,'male','pregnant')])assert.equal(value('iron',profile),null);
for(const key of LunaDRI.keys){
 assert.deepEqual(LunaDRI.get(key,{...p(35,'female','pregnant'),month:1}),LunaDRI.get(key,{...p(35,'female','pregnant'),month:9}));
 assert.deepEqual(LunaDRI.get(key,{...p(35),weight:45}),LunaDRI.get(key,{...p(35),weight:90}));
}
console.log('PASS: DRI reference cases, children and infant boundaries, sex, pregnancy, planning, unsupported profiles, no fabricated month/weight scaling');
