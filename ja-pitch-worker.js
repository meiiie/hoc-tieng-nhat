importScripts('ja-kana.js','ja-pitch.js');
onmessage=({data})=>{try{postMessage({id:data.id,result:JaPitch.analyse(data.pcm,data.sr,data.kana,data.accent)})}catch(e){postMessage({id:data.id,error:String(e.message||e)})}};
