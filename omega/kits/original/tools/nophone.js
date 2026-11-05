// Checks a text for her phone number without the number itself appearing in any file:
// every run of 10–11 digits (spaces or dashes allowed between them) is hashed and compared.
const crypto=require('crypto');
const H=new Set(['09738d9c70e889c10ba8d66ebcdd319cefde57adf841f8d44a628a4edd3d1d95','ae5bde950a29bc17453a1d5d828267337f59413f682833ac4aeefe371b84064a']);
module.exports=function hasPhone(text){
  for(const m of String(text).matchAll(/\d(?:[ \-]?\d){9,14}/g)){
    const d=m[0].replace(/\D/g,'');
    for(let i=0;i+10<=d.length;i++) for(const L of [10,11]){ if(i+L>d.length) continue;
      if(H.has(crypto.createHash('sha256').update(d.slice(i,i+L)).digest('hex'))) return true; }
  }
  return false;
};
