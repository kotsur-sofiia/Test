const assert=require('node:assert/strict'),m=require('../profile-model.js');
assert.equal(m.age('1996-11-02','2026-11-01'),29);assert.equal(m.age('1996-11-02','2026-11-02'),30);assert.equal(m.age('2000-02-29','2025-02-28'),24);assert.equal(m.age('2000-02-29','2025-03-01'),25);
for(const b of ['2026-11-03','2001-02-29','1996-13-01','1996-04-31','1900-01-01',''])assert.equal(m.age(b,'2026-11-02'),null,b);
assert.equal(m.age('2026-10-02','2026-11-02'),0);assert.equal(m.bmi(165,60),22);assert.equal(m.bmi(0,60),null);assert.equal(m.bmi(165,null),null);
console.log('PASS: exact birthday, leap dates, invalid/future/out-of-range DOB, infants, BMI and absent measurements');
