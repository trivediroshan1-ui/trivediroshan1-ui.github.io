from nhi_site import *

SCENES = [
 # (seconds, short title, caption/transcript)
 (9,  'More keys than people', 'Every service account, API key and AI tool login is a machine identity. Most companies hold many more of them than they have people.'),
 (10, 'Many have no owner', 'For a lot of them, nobody knows who owns it, when it ends, or what it can reach. A leaked one can be used for months.'),
 (12, 'A front door for new ones', 'Put a front door in front of new identities. No owner, no scope, no end date, no account. In the lab this stopped the problem when the identity was created.'),
 (12, 'Change secrets in order', 'Update the application first, then change the secret, then check the old one is dead. In one test, five tickets closed and two old secrets still worked.'),
 (11, 'Switch each control off once', 'Then switch each control off, one at a time, and see if anything notices. Eight cases had a control that nothing noticed. Another control was covering it, or it did not matter.'),
 (8,  'What I found', 'I tested 46 cases on made-up data. My guesses were wrong in four places. The data and the script to check it are on the audit page.'),
]

def svg(n):
    H = lambda inner, label: f'<svg viewBox="0 0 1280 720" aria-hidden="true" focusable="false">{inner}</svg>'
    title = lambda t, s='': f'<text class="s-t" x="640" y="92" text-anchor="middle">{E(t)}</text>' + (f'<text class="s-s" x="640" y="134" text-anchor="middle">{E(s)}</text>' if s else '')
    def person(x, y, d):
        return f'<g class="a" style="transition-delay:{d}s"><circle class="p" cx="{x}" cy="{y}" r="26"/><rect class="p" x="{x - 36}" y="{y + 34}" width="72" height="64" rx="30"/></g>'
    def key(x, y, cls='m', d=0, q=None, ok=False):
        g = (f'<g class="a" style="transition-delay:{d}s"><circle class="{cls}" cx="{x}" cy="{y}" r="16"/><rect class="{cls}" x="{x + 14}" y="{y - 4}" width="40" height="8" rx="3"/>'
             f'<rect class="{cls}" x="{x + 36}" y="{y + 2}" width="7" height="14" rx="2"/><circle cx="{x}" cy="{y}" r="6" fill="var(--card)"/>')
        if q:
            g += f'<text class="s-s y" x="{x + 22}" y="{y - 26}" text-anchor="middle" style="font-weight:700">?</text>'
        if ok:
            g += f'<path d="M {x + 10} {y - 28} l 8 9 l 16 -18" fill="none" stroke="var(--good)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
        return g + '</g>'
    if n == 0:
        inner = title('More keys than people', 'Same company, same day')
        inner += ''.join(person(250 + i * 90, 250, round(0.2 + i * .15, 2)) for i in range(4))
        inner += '<text class="s-s" x="430" y="400" text-anchor="middle">people</text>'
        k = ''
        d = 0.6
        for r in range(4):
            for c in range(5):
                k += key(640 + c * 112 - 30, 220 + r * 78, 'm', round(d, 2)); d += .08
        inner += k + '<text class="s-s" x="900" y="560" text-anchor="middle">machine identities</text>'
        return H(inner, '')
    if n == 1:
        inner = title('Many have no owner', 'Who is responsible? Who ends it? What can it reach?')
        d = 0.2
        for r in range(2):
            for c in range(4):
                x = 190 + c * 250; y = 300 + r * 150
                q = (r * 4 + c) not in (1, 6)
                inner += key(x, y, 'm' if not q else 'y', round(d, 2), q=q, ok=not q); d += .22
        inner += '<text class="s-s" x="640" y="610" text-anchor="middle">Amber with ? = no owner on record</text>'
        return H(inner, '')
    if n == 2:
        inner = title('A front door for new ones', 'No owner, no scope, no end date, no account')
        inner += '<rect class="st stp a" x="560" y="200" width="24" height="320" rx="8" style="fill:var(--k);opacity:.25"/><rect class="st stp a" x="700" y="200" width="24" height="320" rx="8" style="fill:var(--k);opacity:.25"/>'
        inner += key(190, 290, 'g', .3, ok=False)
        inner += '<g class="a a2"><rect class="st stg" x="90" y="336" width="360" height="50" rx="10"/><text class="s-s g" x="270" y="371" text-anchor="middle">owner, scope, ends 1 Mar</text></g>'
        inner += '<g class="a a3"><path class="st stg" d="M 470 330 L 540 330" /><path class="st stg" d="M 740 330 L 880 330"/><circle class="g" cx="940" cy="330" r="46"/><path d="M 918 330 l 16 18 l 30 -34" fill="none" stroke="var(--card)" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/></g>'
        inner += key(210, 500, 'r', 1.4)
        inner += '<g class="a a4"><text class="s-s r" x="280" y="560" text-anchor="middle">no owner, no scope</text><path class="st str" d="M 420 500 L 520 500"/><path d="M 536 480 l 40 40 m 0 -40 l -40 40" stroke="var(--bad)" stroke-width="8" stroke-linecap="round"/></g>'
        inner += '<text class="s-s" x="940" y="410" text-anchor="middle">active</text><text class="s-s r" x="760" y="600" text-anchor="middle">refused, with the reason</text>'
        return H(inner, '')
    if n == 3:
        inner = title('Change secrets in order', 'Application first. Then the secret. Then check.')
        steps = [('1', 'Update the app', 'to take the new secret'), ('2', 'Change the secret', 'issue the new value'), ('3', 'Prove the old one is dead', 'try it, expect a refusal')]
        for i, (nn, t, s) in enumerate(steps):
            x = 90 + i * 390
            inner += (f'<g class="a" style="transition-delay:{i * .9}s"><rect class="st {"stg" if i == 2 else "stp"}" x="{x}" y="260" width="330" height="190" rx="22" style="fill:var(--card)"/>'
                      f'<circle class="p" cx="{x + 44}" cy="{ 304}" r="24"/><text x="{x + 44}" y="312" text-anchor="middle" font-size="26" font-weight="700" fill="#031018">{nn}</text>'
                      f'<text class="s-s" x="{x + 165}" y="380" text-anchor="middle" style="fill:var(--ink);font-weight:600">{E(t)}</text><text class="s-s" x="{x + 165}" y="418" text-anchor="middle" style="font-size:22px">{E(s)}</text></g>')
            if i < 2:
                inner += f'<g class="a" style="transition-delay:{i * .9 + .4}s"><path class="st" d="M {x + 336} 355 L {x + 384} 355" marker-end="url(#a4)"/></g>'
        inner += '<defs><marker id="a4" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0 0L10 5L0 10z" fill="var(--mut)"/></marker></defs>'
        inner += '<g class="a a5"><text class="s-s r" x="640" y="560" text-anchor="middle">Skip step 3 and two of five old secrets stayed live</text></g>'
        return H(inner, '')
    if n == 4:
        inner = title('Switch each control off once', 'Did anything notice?')
        rows = [('Control A', True), ('Control B', True), ('Control C', False)]
        for i, (nm, noticed) in enumerate(rows):
            y = 220 + i * 120
            inner += (f'<g class="a" style="transition-delay:{i * .8}s"><text class="s-s" x="170" y="{y + 12}" style="fill:var(--ink)">{nm}</text>'
                      f'<rect class="st" x="360" y="{y - 26}" width="110" height="52" rx="26"/><circle class="m" cx="388" cy="{y}" r="18"/><text class="s-s" x="500" y="{y + 10}">off</text>'
                      f'<path class="st" d="M 580 {y} L 760 {y}" marker-end="url(#a5)"/>'
                      f'<circle class="{ "g" if noticed else "y"}" cx="830" cy="{y}" r="26"/>'
                      f'<text class="s-s" x="880" y="{y + 10}" style="fill:var(--ink)">{"result changed: noticed" if noticed else "nothing changed"}</text></g>')
        inner += '<defs><marker id="a5" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0 0L10 5L0 10z" fill="var(--mut)"/></marker></defs>'
        inner += '<g class="a a5"><text class="s-s y" x="640" y="610" text-anchor="middle">Nothing changed: covered by another control, or it did not matter</text></g>'
        return H(inner, '')
    inner = title('What I found', '46 cases, made-up data, guesses written first')
    nums = [('46', 'cases', 'p'), ('4', 'wrong guesses', 'r'), ('8', 'cases with a control nothing noticed', 'y')]
    for i, (v, t, c) in enumerate(nums):
        x = 220 + i * 420
        lines = ''.join(f'<text class="s-s" x="{x}" y="{420 + j * 34}" text-anchor="middle">{E(ln)}</text>' for j, ln in enumerate(wrap(t, 20)))
        inner += f'<g class="a" style="transition-delay:{i * .7}s"><text x="{x}" y="360" text-anchor="middle" font-size="140" font-weight="700" class="{c}">{v}</text>{lines}</g>'
    inner += '<g class="a a4"><text class="s-s" x="640" y="560" text-anchor="middle" style="fill:var(--ink)">Read the audit. Run the check yourself.</text></g>'
    return H(inner, '')

def build():
    total = sum(s[0] for s in SCENES)
    scenes = ''.join(f'<div class="nex-scene{" on" if i == 0 else ""}" data-s="{i}" data-d="{s[0]}">{svg(i)}</div>' for i, s in enumerate(SCENES))
    dots = ''.join(f'<button type="button" data-go="{i}" aria-label="Scene {i + 1}: {E(s[1])}"{" aria-current=\"true\"" if i == 0 else ""}>{i + 1}</button>' for i, s in enumerate(SCENES))
    trans = ''.join(f'<li><b>{E(s[1])}.</b> {E(s[2])}</li>' for s in SCENES)
    body = f'''<main id="main" class="nhi">
  {subnav('explainer')}
  {hero('Explainer', 'Machine identities in about a minute', f'A short animation of the idea behind the lab: give every machine identity an owner and an end date, change secrets in the right order, and switch each control off once to see if anything notices. {total} seconds, no sound.',
        ['Pause, step or replay at any time', 'Transcript below', 'Respects reduced motion'])}

  <section class="nsec" id="player" aria-labelledby="pl-h">
    <h2 id="pl-h" class="sr-only" style="position:absolute;left:-9999px">Animation</h2>
    <div class="nex nojs" id="nex" role="group" aria-label="Animated explainer, six scenes">
      <div class="nex-stage">{scenes}</div>
      <div class="nex-bar" aria-hidden="true"><i id="nex-bar"></i></div>
      <p class="nex-cap" id="nex-cap">{E(SCENES[0][2])}</p>
      <div class="nex-ctl" hidden id="nex-ctl">
        <button type="button" id="nex-play" aria-pressed="false">Pause</button>
        <button type="button" id="nex-prev">Previous</button>
        <button type="button" id="nex-next">Next</button>
        <button type="button" id="nex-replay">Replay</button>
        <span class="dots" role="group" aria-label="Scenes">{dots}</span>
      </div>
    </div>
    <p class="lede" style="margin-top:12px">If your device is set to reduce motion, the animation starts paused and the scenes do not slide in. Use Next to step through. With scripts off, all six scenes show one after another.</p>
  </section>

  <section class="nsec" id="transcript" aria-labelledby="tr-h">
    <h2 id="tr-h">Transcript</h2>
    <ol class="nex-trans">{trans}</ol>
  </section>

  <section class="nsec" id="more" aria-labelledby="mo-h">
    <h2 id="mo-h">Go further</h2>
    <ul>
      <li>The <a href="/nhi-lab/framework/">framework</a> turns these ideas into seven steps.</li>
      <li>The <a href="/nhi-lab/audit/">audit data</a> has all 46 cases and a script that checks the hashes.</li>
      <li>The same story as a <a href="/assets/share/nhi-lab.mp4">54-second silent video</a> (1.5 MB), for sharing.</li>
    </ul>
    <div class="nnote"><b>Rights and originality</b>All shapes are drawn for this page. There is no audio, no third-party artwork, no logo and no real company data. The numbers come from the lab's made-up data.</div>
  </section>
</main>'''
    desc = 'A one-minute animated explainer of the non-human identity lab: owners and end dates, a front door for new identities, changing secrets in order, and switching each control off once. Pausable, with a transcript.'
    write('nhi-lab/explainer/index.html', shell('nhi-lab/explainer/', 'Machine identities in a minute', desc,
          'Machine identities in about a minute', body, js='nhi-explainer.js', ld=ld_article('Machine identities in a minute', desc, 'nhi-lab/explainer/', 'WebPage')))

if __name__ == '__main__':
    build()
