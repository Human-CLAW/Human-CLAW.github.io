#!/usr/bin/env python3
"""Regenerate the Failure Analysis section of index.html from the error_align deliverable."""
import re, os, json
D=os.path.expanduser('~/Downloads/error_cases_new/deliverable')
SHOW_WHAT_HAPPENS=False   # h3 description line
SHOW_OBJECTIVE=False      # gt facts line
SHOW_FIX=False            # where-it-breaks green box
# ---- hand-written analysis, ONE string per case, shown once below all moments ----
# format: ANALYSIS['case_id'] = "text"
# cut a case video at t seconds (drop the tail); timeline is rescaled to match
VIDEO_TRIM={
 'find_near_but_not_in_view__007': 48.0,   # keep up to step 96 (15x96 frames)
}
# per-case literal replacements applied to the generated moment HTML
POST_FIX={
 'find_ineffective_exploration__011': [
   ("src='static/imgs/errcases/find_ineffective_exploration__011/step_043.jpg'",
    "src='static/imgs/errcases/find_ineffective_exploration__011/step_043.jpg?v=2'"),
 ],
 'nav_unaware_arrived_touch__009': [
   ("<mark class='ok'>The previous action was a failed planner call, and the verifier suggested a small forward movement.</mark> ",
    ""),
 ],
 'nav_unaware_jammed__002': [
   ("<mark class='ok'>The near-body lane is blocked by the chair directly in front</mark>",
    "<mark class='bad'>The near-body lane is blocked by the chair directly in front</mark>"),
   ("<mark class='ok'>Stop/Stand as the goal of touching the chair is achieved</mark>",
    "<mark class='bad'>Stop/Stand as the goal of touching the chair is achieved</mark>"),
 ],
 'nav_lost_target__006': [
   ("<mark class='ok'>The straight-forward path is blocked by a wall/door frame structure immediately ahead</mark>",
    "<mark class='bad'>The straight-forward path is blocked by a wall/door frame structure immediately ahead</mark>"),
 ],
 'find_target_in_view_but_not_seen__019': [
   ("<mark class='ok'>The forward lane has a chair, which would cause a collision</mark>",
    "<mark class='bad'>The forward lane has a chair, which would cause a collision</mark>"),
 ],
 'find_unaware_jammed__003': [
   ("<mark class='ok'>The humanoid is positioned directly in front of the stairs, with the first step at its feet</mark>",
    "<mark class='bad'>The humanoid is positioned directly in front of the stairs, with the first step at its feet</mark>"),
 ],
 'find_midpoint_give_up__020': [
   ("<span class='fl'>verifier → Turn&lt;right&gt;&lt;90&gt;:</span>",
    "<span class='fl'>verifier → <mark class='bad'>Turn&lt;right&gt;&lt;90&gt;</mark>:</span>"),
 ],
}
ANALYSIS={
 'find_ineffective_actions__017':
   "At step 56 the agent decides to turn left, and at step 57 it decides to "
   "turn right, back to where it was just facing. It keeps spinning in place "
   "like this because it has no awareness of its own recent actions.",
 'find_ineffective_exploration__011':
   "The agent spends all 100 steps searching outdoors. It never makes the "
   "simple inference that a chair is far more likely to be found inside the "
   "house.",
 'find_midpoint_give_up__020':
   "At step 49, the verifier's analysis is correct &mdash; there is a wall "
   "ahead &mdash; but its conclusion to turn right is wrong. After the turn, "
   "at steps 50 and 51, the agent completely confuses its earlier goal and "
   "direction, and ends up walking back the way it came.",
 'find_near_but_not_in_view__007':
   "The bed is actually just behind the agent, to its rear right. If it had "
   "looked around at the start instead of rushing down the path ahead, it "
   "would have found the bed immediately.",
 'find_target_in_view_but_not_seen__019':
   "The agent never sees the yellow couch that the arrow points to. The "
   "verifier then hallucinates the distance to the chair ahead and turns the "
   "agent away, throwing away the chance completely.",
 'nav_lost_target__006':
   "The verifier misjudges where the agent's own body is, which forces an "
   "unnecessary turn. In the steps that follow, the agent does not have the "
   "spatial ability to find its way back to the target.",
 'nav_stop_while_far__009':
   "The agent fails to understand where its own body is &mdash; it declares "
   "that it is &ldquo;touching&rdquo; the target while there is still clear "
   "distance left.",
 'nav_target_hallucination__012':
   "The instruction clearly states that the target is a chair. Later in the "
   "episode the agent starts to hallucinate: it calls the target a "
   "&ldquo;chair/bed&rdquo; and claims that it can see it.",
 'nav_unaware_jammed__002':
   "The agent never realizes that it is actually blocked by the table; it "
   "claims it is blocked by the chair (even though the action it picks is a "
   "correct one). The verifier, however, judges that the chair is still some "
   "distance away and chooses to keep going.",
 'nav_unaware_arrived_touch__009':
   "The agent only registers that the chair is &ldquo;very close&rdquo; and "
   "believes there is still a gap left, yet in the ego view its body and the "
   "chair already overlap. This is a failure of body-to-object spatial "
   "awareness.",
 'interact_sit_on_air__011':
   "At step 86 the couch is still clearly visible, but the agent "
   "misunderstands where the couch is relative to its own body &mdash; it "
   "claims the couch is behind it &mdash; and sits straight into the air.",
 'interact_sit_wrong__004':
   "The agent does turn its body around, but not to the right orientation. "
   "It can see the bed and believes it is about to sit on it &mdash; instead "
   "it sits down on the bedside table.",
 'interact_stand_after_sit__007':
   "At step 26 the agent has already sat down on the toilet successfully. At "
   "step 27 the verifier &mdash; the same VLM &mdash; fails to understand its "
   "own sitting posture (it believes the agent is standing), sees the sink in "
   "front, concludes the agent is not on the toilet, and sends it off to "
   "search again.",
 'find_unaware_jammed__003':
   "This is a spiral staircase, and the agent is stuck on the outside of the "
   "railing the whole time. It does not know where it is, and it never "
   "realizes that it is blocked.",
}
cases=json.load(open(D+'/error_cases.json'))['cases']
EXCLUDE={'interact_stop_but_never_sit__003','find_too_far__011'}
cases=[c for c in cases if c['case_id'] not in EXCLUDE]
OLD1=os.path.expanduser('~/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/wxid_wwmseivh4cou12_8f7a/msg/file/2026-07/humanclaw_error_align/deliverable')
OVERRIDES={
 'nav_unaware_jammed__002': OLD1+'/cases/nav_unaware_jammed__002.html',
}
MOMENT_KEEP={
 'nav_unaware_jammed__002': ['86'],   # keep only these step numbers
 'find_target_in_view_but_not_seen__019': ['15'],
 'nav_lost_target__006': ['36'],
}
FRAME_ROOTS=[D+'/frames', os.path.dirname(D)+'/frames/ego', os.path.dirname(D)+'/out/frames', OLD1+'/frames']
MODEL={'gemini25':'Gemini-2.5','gemini31':'Gemini-3.1','qwen36_27b':'Qwen3.6-27B','qwen36_35b_a3b':'Qwen3.6-35B-A3B',
       'gemma4':'Gemma-4-31B','internvl35_38b':'InternVL3.5-38B','claude48':'Claude-4.8','qwen35_27b':'Qwen3.5-27B','gpt55low':'GPT-5.5'}
NAMES={'ineffective_actions':'Ineffective actions','ineffective_exploration':'Ineffective exploration',
   'midpoint_give_up':'Midpoint give up','near_but_not_in_view':'Near but not in view',
   'target_in_view_but_not_seen':'In view not seen','too_far':'Too far','unaware_jammed':'Unaware jammed',
   'lost_target':'Lost target','stop_while_far':'Stop while far','target_hallucination':'Target hallucination',
   'unaware_arrived_touch':'Unaware arrived/touch','sit_on_air':'Sit on air','sit_wrong':'Sit wrong',
   'stand_after_sit':'Stand after sit','stop_but_never_sit':'Stop but never sit'}
NAV={'chair','tv','potted_plant'}
mo_pat=re.compile(
 r"<div class='mo'><div class='mo-top'>\n"
 r"<div class='shot' data-t='([^']*)'>(.*?)<div class='stamp'>(.*?)</div></div>\n"
 r"<div><h3>(.*?)</h3>(?:<div class='gt'>(.*?)</div>)?</div>\n</div>\n"
 r"(?:<div class='stack'>\n(.*?)\n</div>\n)?"
 r"(?:<div class='key'[^>]*>.*?</div>\n)?"
 r"<div class='fix'>(.*?)</div>\n</div>", re.S)
row_pat=re.compile(r"<div class='row( act| ver)?'><div class='lab'>(.*?)</div><div class='val'>(.*?)</div></div>")

tabs=[]; contents=[]
for i,c in enumerate(cases):
    cid=c['case_id']
    src=open(OVERRIDES.get(cid, f"{D}/cases/{cid}.html")).read()
    import shutil as _sh0
    dstv=f"static/videos/errcases/{cid}.mp4"
    if cid in VIDEO_TRIM:
        import imageio_ffmpeg, subprocess
        ff=imageio_ffmpeg.get_ffmpeg_exe()
        subprocess.run([ff,'-y','-loglevel','error','-i',f"{D}/videos/{cid}.mp4",
                        '-t',str(VIDEO_TRIM[cid]),'-c:v','libx264','-preset','veryfast',
                        '-crf','21','-pix_fmt','yuv420p','-an',dstv],check=True)
    else:
        _sh0.copy(f"{D}/videos/{cid}.mp4", dstv)
    tlm=re.search(r"(<div class='tl' data-dur='[^']*'>.*?</div>)\n(<div class='key'>.*?</div>)", src, re.S)
    assert tlm, cid
    tl, tlkey = tlm.group(1), tlm.group(2)
    tl=re.sub(r"<div class='seg'[^>]*></div>\n?","",tl)
    tl=re.sub(r"<div class='vis'[^>]*></div>\n?","",tl)
    if cid in VIDEO_TRIM:
        _od=float(re.search(r"data-dur='([^']*)'",tl).group(1)); _nd=VIDEO_TRIM[cid]; _r=_od/_nd
        tl=re.sub(r"data-dur='[^']*'",f"data-dur='{_nd}'",tl)
        tl=re.sub(r"left:([0-9.]+)%",lambda m: f"left:{min(100.0,float(m.group(1))*_r):.2f}%",tl)
    tlkey="<div class='key'><span><i style='background:#a3282a;width:3px'></i>key moment</span><span>click to seek</span></div>" 
    mos=mo_pat.findall(src)
    if cid in OVERRIDES: assert len(mos)>=1, cid
    else: assert len(mos)==len(c['moments']), (cid, len(mos), len(c['moments']))
    if cid in MOMENT_KEEP:
        keep=MOMENT_KEEP[cid]
        mos=[m for m in mos if re.search(r"step (\d+)", m[2]) and re.search(r"step (\d+)", m[2]).group(1) in keep]
        assert mos, (cid, 'moment filter emptied')
    mo_html=[]
    for mi,(t, shot_inner, stamp, h3, gt, stack, fix) in enumerate(mos):
        import shutil as _sh
        for img in re.findall(r"src='\.\./frames/([^']*)'", shot_inner):
            dst=f"static/imgs/errcases/{img}"
            if os.path.exists(dst): continue   # keep locally edited frames
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            for r in FRAME_ROOTS:
                if os.path.exists(f"{r}/{img}"): _sh.copy(f"{r}/{img}", dst); break
            assert os.path.exists(dst), img
        shot_inner=shot_inner.replace("../frames/","static/imgs/errcases/").strip()
        # keep only the ego frame: drop panel labels and top-down/third-person images
        shot_inner=re.sub(r"<div class='panlab'>.*?</div>","",shot_inner)
        shot_inner=re.sub(r"<img src='[^']*/(?:top_|third_)[^']*'[^>]*>","",shot_inner).strip()
        stamp=re.sub(r"\s*&nbsp;·&nbsp;\s*d = [0-9.]+ m","",stamp)
        parts=[]
        if SHOW_WHAT_HAPPENS: parts.append(f"<h3>{h3}</h3>")
        if SHOW_OBJECTIVE and gt: parts.append(f"<div class='gt'>{gt}</div>")
        fixblock=f"<div class='fix'>{fix}</div>" if SHOW_FIX else ""
        analblock=""
        if stack:
            rows=row_pat.findall(stack)
            flds=[f"<p class='fld{(' '+cls.strip()) if cls.strip() else ''}'><span class='fl'>{lab}:</span> {val}</p>"
                  for cls,lab,val in rows
                  if not (cls.strip()=='ver' and lab.strip()=='verifier')]
            parts.append(f"<div class='flds'>\n{chr(10).join(flds)}\n</div>")
            mo_html.append(f"""<div class='mo'><div class='mo-top'>
<div class='shot' data-t='{t}'>{shot_inner}<div class='stamp'>{stamp}</div></div>
<div>{chr(10).join(parts)}</div>
</div>
{analblock}{fixblock}
</div>""")
        else:
            if fixblock: parts.append(fixblock)
            inner=chr(10).join(parts)
            right=f"<div>{inner}</div>" if inner.strip() else ""
            cls="mo-top" if right else "mo-top mo-solo"
            mo_html.append(f"""<div class='mo'><div class='{cls}'>
<div class='shot' data-t='{t}'>{shot_inner}<div class='stamp'>{stamp}</div></div>
{right}
</div>
{analblock}
</div>"""  )
    for _old,_new in POST_FIX.get(cid,[]):
        mo_html=[m.replace(_old,_new) for m in mo_html]
    case_anal=ANALYSIS.get(cid,"")
    if case_anal:
        mo_html.append(f"<div class='anal case-anal'><span class='fl'>analysis:</span> {case_anal}</div>")
    stage,bucket=cid.split('_',1)[0], cid.split('_',1)[1].rsplit('__',1)[0]
    tabs.append(f"""      <div class="tldr-card collapsible err-tab" onclick="errSelect({i})">
        <div class="card-head"><div>
          <div class="tag-line">{stage.capitalize()}</div>
          <h4>{NAMES[bucket]}</h4>
        </div><i class="fas fa-chevron-down fold-icon"></i></div>
      </div>""")
    obj=c['object']; disp=obj.replace('_',' ')
    instr=f"find a <b>{disp}</b> and navigate to it" if obj in NAV else f"find a <b>{disp}</b>, navigate to it, and sit on it"
    contents.append(f"""        <div class="err-content" data-i="{i}" style="display:none">
          <div class="err-chip"><span class="err-chip-model">{MODEL[c['model']]}</span><span class="err-chip-sep">&middot;</span><span>&ldquo;{instr}&rdquo;</span></div>
          <video class="err-video" muted playsinline controls preload="metadata">
            <source src="static/videos/errcases/{cid}.mp4" type="video/mp4" /></video>
          {tl}
          {tlkey}
          <div class="err-legend"><span><mark class='bad'>red highlight</mark> = incorrect claim</span><span><mark class='ok'>green highlight</mark> = correct</span></div>
          <div class="err-analysis">
{chr(10).join(mo_html)}
          </div>
        </div>""")

s=open('index.html').read()
a=s.find('<section class="section section-alt" id="failure-gallery">')
b=s.find('</section>', a); assert a!=-1 and b!=-1
b+=len('</section>')
section=f"""<section class="section section-alt" id="failure-gallery">
  <div class="container is-max-widescreen has-text-centered">
    <h2 class="title is-3">Failure Examples &amp; Analysis</h2>
    <div class="err-tabs" id="errTabs">
{chr(10).join(tabs)}
    </div>
    <div class="fw-panel err-panel" id="errPanel">
      <div class="fw-panel-inner">
{chr(10).join(contents)}
      </div>
    </div>
  </div>
</section>"""
s=s[:a]+section+s[b:]
open('index.html','w').write(s)
print(f"failure section regenerated: {len(cases)} cases")
