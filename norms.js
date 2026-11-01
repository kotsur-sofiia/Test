/* DRI RDA/AI reference tables; sodium and potassium use the 2019 update.
   General dietary references, not supplement prescriptions or clinical targets.
   Age columns: 0–6 mo, 7–12 mo, 1–3 y, 4–8 y, 9–13 y, 14–18 y,
   19–30 y, 31–50 y, 51–70 y, 71+ y. Sex pairs are [male,female]. */
'use strict';
(() => {
 const rows={
 calcium:[200,260,700,1000,1300,1300,1000,1000,[1000,1200],1200],
 magnesium:[30,75,80,130,240,[410,360],[400,310],[420,320],[420,320],[420,320]],
 potassium:[400,860,2000,2300,[2500,2300],[3000,2300],[3400,2600],[3400,2600],[3400,2600],[3400,2600]],
 phosphorus:[100,275,460,500,1250,1250,700,700,700,700],
 iron:[.27,11,7,10,8,[11,15],[8,18],[8,18],8,8],
 zinc:[2,3,3,5,8,[11,9],[11,8],[11,8],[11,8],[11,8]],
 c:[40,50,15,25,45,[75,65],[90,75],[90,75],[90,75],[90,75]],
 b12:[.4,.5,.9,1.2,1.8,2.4,2.4,2.4,2.4,2.4],
 folate:[65,80,150,200,300,400,400,400,400,400],
 fiber:[null,null,19,25,[31,26],[38,26],[38,25],[38,25],[30,21],[30,21]],
 a:[400,500,300,400,600,[900,700],[900,700],[900,700],[900,700],[900,700]],
 d:[10,10,15,15,15,15,15,15,15,20],
 e:[4,5,6,7,11,15,15,15,15,15],
 k:[2,2.5,30,55,60,75,[120,90],[120,90],[120,90],[120,90]],
 b1:[.2,.3,.5,.6,.9,[1.2,1],[1.2,1.1],[1.2,1.1],[1.2,1.1],[1.2,1.1]],
 b2:[.3,.4,.5,.6,.9,[1.3,1],[1.3,1.1],[1.3,1.1],[1.3,1.1],[1.3,1.1]],
 b3:[2,4,6,8,12,[16,14],[16,14],[16,14],[16,14],[16,14]],
 b5:[1.7,1.8,2,3,4,5,5,5,5,5],
 b6:[.1,.3,.5,.6,1,[1.3,1.2],1.3,1.3,[1.7,1.5],[1.7,1.5]],
 iodine:[110,130,90,90,120,150,150,150,150,150],
 copper:[200,220,340,440,700,890,900,900,900,900],
 manganese:[.003,.6,1.2,1.5,[1.9,1.6],[2.2,1.6],[2.3,1.8],[2.3,1.8],[2.3,1.8],[2.3,1.8]],
 selenium:[15,20,20,30,40,55,55,55,55,55],
 choline:[125,150,200,250,375,[550,400],[550,425],[550,425],[550,425],[550,425]],
 sodium:[110,370,800,1000,1200,1500,1500,1500,1500,1500],
 chloride:[180,570,1500,1900,2300,2300,2300,2300,2000,1800],
 fluoride:[.01,.5,.7,1,2,3,[4,3],[4,3],[4,3],[4,3]],
 molybdenum:[2,3,17,22,34,43,45,45,45,45],
 chromium:[.2,5.5,11,15,[25,21],[35,24],[35,25],[35,25],[30,20],[30,20]],
 ala:[null,null,.7,.9,[1.2,1],[1.6,1.1],[1.6,1.1],[1.6,1.1],[1.6,1.1],[1.6,1.1]],
 la:[4.4,4.6,7,10,[12,10],[16,11],[17,12],[17,12],[14,11],[14,11]],
 biotin:[5,6,8,12,20,25,30,30,30,30]
 };
 // Pregnancy columns: 14–18, 19–30, 31–50. These references do not vary by month.
 const pregnancy={calcium:[1300,1000,1000],magnesium:[400,350,360],potassium:[2600,2900,2900],phosphorus:[1250,700,700],iron:[27,27,27],zinc:[12,11,11],c:[80,85,85],b12:[2.6,2.6,2.6],folate:[600,600,600],fiber:[28,28,28],a:[750,770,770],d:[15,15,15],e:[15,15,15],k:[75,90,90],b1:[1.4,1.4,1.4],b2:[1.4,1.4,1.4],b3:[18,18,18],b5:[6,6,6],b6:[1.9,1.9,1.9],iodine:[220,220,220],copper:[1000,1000,1000],manganese:[2,2,2],selenium:[60,60,60],choline:[450,450,450],sodium:[1500,1500,1500],chloride:[2300,2300,2300],fluoride:[3,3,3],molybdenum:[50,50,50],chromium:[29,30,30],ala:[1.4,1.4,1.4],la:[13,13,13],biotin:[30,30,30]};
 const ai=new Set(['fiber','k','b5','biotin','potassium','sodium','chloride','fluoride','chromium','manganese','choline','ala','la']);
 function ageYears(p){if(!p||!Number.isInteger(p.age)||p.age<0||!['years','months'].includes(p.ageUnit))return null;if(p.ageUnit==='months')return p.age<=23?p.age/12:null;return p.age>=1&&p.age<=120?p.age:null;}
 function group(p){const age=ageYears(p);if(age===null||!['female','male'].includes(p.sex))return null;if(age<1)return p.age<=6?0:1;return age<4?2:age<9?3:age<14?4:age<19?5:age<31?6:age<51?7:age<71?8:9;}
 function get(key,p){const g=group(p);if(g===null||!rows[key]||(key==='b3'&&g===0))return null;let value;if(p.status==='pregnant'){const age=ageYears(p);if(p.sex!=='female'||age<14||age>50)return null;value=pregnancy[key]?.[age<19?0:age<31?1:2]??null;}else{const raw=rows[key][g];value=Array.isArray(raw)?raw[p.sex==='male'?0:1]:raw;}if(value===null||value===undefined)return null;return {value,type:g===0||(g===1&&!['iron','zinc'].includes(key))||ai.has(key)?'AI':'RDA'};}
 globalThis.LunaDRI=Object.freeze({get,ageYears,group,keys:Object.freeze(Object.keys(rows)),version:'DRI-reference-v1-NaK2019'});
})();
