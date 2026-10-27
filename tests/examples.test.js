const test=require('node:test'),assert=require('node:assert/strict');
const E=require('../ja-examples');
const example={text:'学校へ行く。',match:{start:0,end:2,surface:'学校'},translation:{text:'Tôi đi học.',id:2,username:'translator',machine:false,pivot:false,from:{id:3,username:'English author'},via:{id:3,username:'English author'}},id:1,username:'author',url:'https://tatoeba.org/sentences/show/1',license:'CC BY 2.0 FR'};
test('cloze removes only the matched surface and retains the rest of the sentence',()=>{
 assert.deepEqual(E.cloze({kanji:'学校',kana:'がっこう',example}),{before:'',ans:'学校',after:'へ行く。'});
 assert.equal(E.cloze({example:null}),null);
 assert.equal(E.cloze({example:{...example,match:{start:1,end:3,surface:'学校'}}}),null);
});
test('example output labels pivot and machine translations and escapes text/attribution',()=>{
 for(const [translation,label] of [[{machine:true,pivot:false},'bản dịch máy, cần kiểm tra'],[{machine:false,pivot:true},'dịch qua câu tiếng Anh']]){
  const html=E.render({...example,username:'<img>',translation:{...example.translation,...translation}});
  assert.ok(html.includes(label));assert.ok(html.includes('&lt;img&gt;'));assert.ok(!html.includes('<img>'));
  assert.ok(html.includes('https://tatoeba.org/sentences/show/1'));assert.ok(html.includes('CC BY 2.0 FR'));
 }
});
