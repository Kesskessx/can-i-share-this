#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / 'dist' / 'index.html'

STYLE = r'''
<style id="cist-result-feedback-style">
.result-feedback{display:none;margin-top:18px;padding-top:16px;border-top:1px solid var(--line);text-align:left}
.result-feedback.show{display:block}
.result-feedback-question{margin:0;color:var(--text);font-size:13px;font-weight:850}
.result-feedback-votes,.result-feedback-reasons{display:flex;gap:7px;flex-wrap:wrap;margin-top:9px}
.result-feedback button{min-height:36px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--text);padding:7px 11px;font:inherit;font-size:12px;font-weight:750;cursor:pointer}
.result-feedback button:hover{background:var(--soft)}
.result-feedback button:focus-visible{outline:3px solid color-mix(in srgb,var(--cist-accent,#6578e8) 42%,transparent);outline-offset:2px}
.result-feedback button:disabled{cursor:default;opacity:.58}
.result-feedback-reasons[hidden],.result-feedback-votes[hidden]{display:none!important}
.result-feedback-status{margin:9px 0 0;color:var(--muted);font-size:12px;line-height:1.4}
@media(max-width:600px){.result-feedback{margin-top:15px;padding-top:14px}.result-feedback button{flex:1 1 calc(50% - 7px)}}
</style>
'''

SCRIPT = r'''
<script id="cist-result-feedback-script">
(function(){
  var card=document.getElementById('result-card'),result=document.getElementById('result'),input=document.getElementById('url');
  if(!card||!result||!input)return;
  var box=document.createElement('section');
  box.className='result-feedback';box.id='result-feedback';box.setAttribute('aria-labelledby','result-feedback-question');
  box.innerHTML='<p class="result-feedback-question" id="result-feedback-question">Was this result helpful?</p><div class="result-feedback-votes"><button type="button" data-vote="yes">Yes</button><button type="button" data-vote="no">No</button></div><div class="result-feedback-reasons" hidden><button type="button" data-reason="wrong_verdict">Wrong verdict</button><button type="button" data-reason="wrong_destination">Wrong destination</button><button type="button" data-reason="unclear_explanation">Unclear explanation</button><button type="button" data-reason="incomplete_scan">Incomplete scan</button></div><p class="result-feedback-status" role="status" aria-live="polite"></p>';
  card.appendChild(box);
  var votes=box.querySelector('.result-feedback-votes'),reasons=box.querySelector('.result-feedback-reasons'),statusText=box.querySelector('.result-feedback-status');
  var submitted=false;
  function value(){return String(input.value||'').trim()}
  function inputType(){
    var v=value().replace(/^mailto:/i,'');
    if(/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v))return'email';
    if(/^(0x[0-9a-fA-F]{40}|bc1[ac-hj-np-z02-9]{20,90}|ltc1[ac-hj-np-z02-9]{20,90}|T[1-9A-HJ-NP-Za-km-z]{33}|[1-9A-HJ-NP-Za-km-z]{32,44})$/.test(v))return'crypto';
    if(!/^https?:\/\//i.test(v)&&(/\s/.test(v)||v.length>180))return'message';
    return'link';
  }
  function verdictStatus(){
    if(card.classList.contains('status-high'))return'high';
    if(card.classList.contains('status-caution'))return'caution';
    if(card.classList.contains('status-low'))return'low';
    return'unknown';
  }
  function signalCount(){var list=document.getElementById('signals');return Math.min(6,list?list.querySelectorAll('li').length:0)}
  function reset(){submitted=false;box.classList.remove('show');votes.hidden=false;reasons.hidden=true;statusText.textContent='';box.querySelectorAll('button').forEach(function(button){button.disabled=false})}
  function show(){if(result.classList.contains('hidden')||submitted)return;if(document.body.classList.contains('cist-full-scan-running'))return;box.classList.add('show')}
  async function submit(vote,reason){
    if(submitted)return;submitted=true;box.querySelectorAll('button').forEach(function(button){button.disabled=true});
    try{
      var response=await fetch('/api/feedback',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({vote:vote,reason:reason||null,input_type:inputType(),status:verdictStatus(),signal_count:signalCount()}),keepalive:true});
      if(!response.ok)throw new Error('Feedback request failed');
      votes.hidden=true;reasons.hidden=true;statusText.textContent='Thanks — your feedback was recorded.';
    }catch(_){submitted=false;box.querySelectorAll('button').forEach(function(button){button.disabled=false});statusText.textContent='Feedback could not be recorded. Please try again.'}
  }
  votes.addEventListener('click',function(event){var button=event.target.closest('[data-vote]');if(!button)return;if(button.dataset.vote==='yes')submit('yes',null);else{votes.hidden=true;reasons.hidden=false;reasons.querySelector('button').focus()}});
  reasons.addEventListener('click',function(event){var button=event.target.closest('[data-reason]');if(button)submit('no',button.dataset.reason)});
  input.addEventListener('input',reset);var form=document.getElementById('scan-form');if(form)form.addEventListener('submit',reset,true);var again=document.getElementById('again');if(again)again.addEventListener('click',reset);
  document.addEventListener('cist:result-updated',function(){setTimeout(show,0)});
  var reputation=document.getElementById('reputation');if(reputation)new MutationObserver(function(){setTimeout(show,0)}).observe(reputation,{attributes:true,attributeFilter:['class']});
})();
</script>
'''


def main():
    if not HOME.is_file():
        raise RuntimeError('Homepage not found')
    source = HOME.read_text(encoding='utf-8')
    if 'id="cist-result-feedback-style"' in source or 'id="cist-result-feedback-script"' in source:
        raise RuntimeError('Result feedback already applied')
    if '</head>' not in source or '</body>' not in source:
        raise RuntimeError('Invalid homepage document')
    source = source.replace('</head>', STYLE + '\n</head>', 1)
    source = source.replace('</body>', SCRIPT + '\n</body>', 1)
    required = [
        'Was this result helpful?',
        '/api/feedback',
        'wrong_verdict',
        'wrong_destination',
        'unclear_explanation',
        'incomplete_scan',
        'input_type:inputType()',
        'signal_count:signalCount()',
    ]
    forbidden = ['url:', 'hostname:', 'message:', 'crypto_address:']
    for token in required:
        if token not in source:
            raise RuntimeError(f'Result feedback guard failed: missing {token}')
    feedback_source = source[source.index('<script id="cist-result-feedback-script">'):]
    for token in forbidden:
        if token in feedback_source:
            raise RuntimeError(f'Result feedback privacy guard failed: forbidden {token}')
    HOME.write_text(source, encoding='utf-8')
    print('Applied anonymous result feedback UI')


if __name__ == '__main__':
    main()
