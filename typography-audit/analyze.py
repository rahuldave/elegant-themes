"""Score the captured SmallDocs specimens. All thresholds are review choices."""
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = json.loads((ROOT / 'measurements.json').read_text())
THEMES = json.loads((ROOT / 'themes.json').read_text())
MAXIMA = dict(font=15, size=10, leading=20, measure=15, space=10, hierarchy=10, code=10, color=10)

def px(v):
    return float(v.removesuffix('px'))

def rgba(s):
    c = [float(v) for v in re.findall(r'[\d.]+', s)]
    if s.startswith('color(srgb '):
        c[:3]=[v*255 for v in c[:3]]
    return c[:3] + ([c[3]] if len(c) == 4 else [1])

def mix(top, bottom):
    return [top[i]*top[3] + bottom[i]*(1-top[3]) for i in range(3)] + [1]

def luminance(c):
    values = [v/255 for v in c[:3]]
    linear = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in values]
    return sum(a*b for a,b in zip(linear, [.2126,.7152,.0722]))

def contrast(a,b):
    a,b=sorted([luminance(a),luminance(b)])
    return (b+.05)/(a+.05)

def contrast_range(item, record, bounds=None):
    """Composite ancestor solids; sample CSS gradient beneath the reading column."""
    backgrounds=item['backgrounds']
    gradient=next((b for b in backgrounds if 'linear-gradient(' in b['image']),None)
    bases=[[255,255,255,1]]
    if gradient:
        stops=[rgba(c) for c in re.findall(r'rgba?\([^)]*\)', gradient['image'])]
        if '90deg' in gradient['image'] and len(stops)==3:
            left,right=(bounds or (0,record['viewport']['width']))
            bases=[]
            for j in range(101):
                t=(left+(right-left)*j/100)/record['viewport']['width']
                index=min(int(t*2),1); f=t*2-index
                bases.append([stops[index][i]*(1-f)+stops[index+1][i]*f for i in range(3)]+[1])
        else:
            bases=stops # conservative range for the subtle vertical Vapor gradient
    ratios=[]
    for base in bases:
        bg=[255,255,255,1]
        for b in reversed(backgrounds):
            bg=mix(rgba(b['background']),bg)
            if gradient and b['tag'] == gradient['tag'] and b['cls']==gradient['cls']:
                bg=mix(base,bg)
        foreground=mix(rgba(item['style']['color']),bg)
        ratios.append(contrast(foreground,bg))
    return [round(min(ratios),3),round(max(ratios),3)]

def full_measure(record):
    values=[line['chars'] for p in record['paragraphs'] for line in p['lines'][:-1]]
    return sum(values)/len(values)

def all_measure(record):
    values=[line['chars'] for p in record['paragraphs'] for line in p['lines']]
    return sum(values)/len(values)

def leading_score(value):
    if 1.1999<=value<=1.4501:return 20
    if 1.4501<value<=1.55:return 17
    if 1.55<value<=1.65:return 12
    if 1.65<value<=1.8:return 7
    if 1.1<=value<1.2:return 12
    return 3

def measure_score(value):
    if 45<=value<=90:return 10
    if 40<=value<45 or 90<value<=100:return 8
    if 35<=value<40 or 100<value<=110:return 5
    if 30<=value<35 or 110<value<=120:return 2
    return 0

FONT = {
 'folio':(15,'Source Serif 4 is a calm text face; Caslon is reserved for display.'),
 'atelier':(15,'DM Sans gives prose and interface a consistent, quiet voice.'),
 'nocturne':(15,'Source Serif 4 carries prose, with a distinct monospace role for code.'),
 'tufte':(15,'ET Book is purposefully literary, with visibly distinct emphasis.'),
 'bootstrap':(12,'A capable system stack, though less deliberate in identity than Butterick prefers.'),
 'cerulean':(12,'Readable system text; the generic stack offers little typographic character.'),
 'journal':(12,'System body text remains generic despite the expressive heading family.'),
 'litera':(14,'Georgia is a convincing text face here; the serif/sans switch in lists needs attention.'),
 'lux':(10,'One-pixel tracking spreads lowercase body text; weight 300 is delicate for small UI.'),
 'minty':(12,'Capable system text, with little distinct typographic identity.'),
 'morph':(14,'Nunito is a legible, soft sans; its color is scored separately.'),
 'pulse':(12,'A familiar system stack, with identity supplied mainly by color.'),
 'quartz':(12,'A capable system stack; the vivid surface is assessed separately.'),
 'sketchy':(6,'Neucha handwriting and Cabin Sketch headings conflict with sustained technical reading.'),
 'slate':(12,'System text is functional; the visual theme carries the personality.'),
 'vapor':(10,'Lato is suitable, but a glow on every line softens the apparent edges of small type.'),
}

NOTES = {
 'folio':('Refine','Keep the CRBooks character. Tighten prose leading, reduce the display hierarchy, and enlarge code on phones.'),
 'atelier':('Refine','Strong studio identity. Tighten leading and paragraph gaps; keep the rule and teal accents.'),
 'nocturne':('Refine','A strong dark reading palette. Tighten leading and raise mobile code size; keep the brass restrained.'),
 'tufte':('Keep as reference','Best Butterick alignment here. Italic section headings and a large title remain conscious exceptions.'),
 'bootstrap':('Baseline','Useful as a control. Narrow the prose column and soften the title scale before treating it as a reading theme.'),
 'cerulean':('Optional','Readable prose, but blue links and headings need stronger contrast on white; little editorial distinction.'),
 'cosmo':('Alternate','A clean sans option. The 102-character desktop measure needs narrowing; link contrast is also close to the threshold.'),
 'cyborg':('Alternate dark','Good body contrast. Its black/cyan character is more technical than bookish; narrow the text column.'),
 'darkly':('Conditional · dark','The most straightforward dark Bootswatch candidate for documentation. Narrow the prose and repair colored messages and the outline button.'),
 'flatly':('Conditional · sans','A restrained sans option with dependable structure. Darken teal links and narrow the default SmallDocs prose column.'),
 'journal':('Alternate','Expressive headings are attractive, but not enough to give the system-font body a complete editorial voice.'),
 'litera':('Shortlist · prose','The strongest Bootswatch reading option here. Preserve Georgia, but unify list typography and check blue links.'),
 'lumen':('Alternate','Clean and usable; the desktop measure is too wide and links need darkening.'),
 'lux':('Special use','Keep for short, formal pages. Remove lowercase tracking, strengthen small text, and avoid all-cap section headings for docs.'),
 'materia':('Alternate','Solid functional UI; the blue link treatment is too light for normal text. Less distinct as an editorial theme.'),
 'minty':('Avoid as-is','The pale body and pastel links sacrifice reading contrast. Preserve the palette only after darkening text and links.'),
 'morph':('Avoid as-is','Low body contrast and soft relief weaken the reading surface. It needs a substantial contrast pass.'),
 'pulse':('Alternate','A sound light alternative when purple is wanted. Narrow the prose; the main reading surface is otherwise conventional.'),
 'quartz':('Avoid for long docs','White text crosses a changing gradient, and inline code is hard to read. Put long prose on a solid surface.'),
 'sandstone':('Alternate','Readable body with earthy accents. The theme still needs a narrower prose measure and darker links.'),
 'simplex':('Alternate','A quiet red-accent option. Small width and leading adjustments would make it a dependable documentation theme.'),
 'sketchy':('Special use','Excellent for a playful sketchbook; handwriting and rough display faces are a poor match for long technical prose.'),
 'slate':('Alternate dark','A usable muted dark option. Gradients and embossed controls add weight; the desktop prose measure is long.'),
 'solar':('Conditional dark','A quieter dark personality. Body contrast is only 4.75:1 and the desktop prose measure is long; preserve contrast when refining.'),
 'spacelab':('Conditional','The body grey is just below 4.5:1 on white. Darken it before considering it for everyday reading.'),
 'superhero':('Alternate dark','Legible dark prose and code. Its stronger orange/blue palette suits technical content more than a book.'),
 'united':('Alternate','Ubuntu gives a recognizable voice. The orange links need darkening, and the prose column can be narrower.'),
 'vapor':('Special use','A convincing neon aesthetic, but pervasive glow and saturated body text compete with long-form reading.'),
 'yeti':('Alternate','A clean light workhorse. It is useful where a neutral presentation is wanted, after narrowing the prose and darkening links.'),
 'zephyr':('Shortlist · modern UI','Inter, a quiet canvas, and restrained components make a good modern alternative. Keep prose narrower than controls.'),
}

# Editorial observations, independent of the Butterick point bands.
# Hierarchy /25, spacing /20, layout /15, surfaces /10, personality /10.
DESIGN = {
 'folio':(20,16,11,9,10), 'atelier':(23,17,11,9,10),
 'nocturne':(22,17,11,9,10), 'tufte':(22,18,14,9,9),
 'bootstrap':(20,17,12,8,5), 'cerulean':(19,17,12,7,6),
 'cosmo':(20,17,11,8,7), 'cyborg':(20,17,12,7,7),
 'darkly':(21,17,12,8,8), 'flatly':(21,17,12,8,7),
 'journal':(21,17,12,8,8), 'litera':(21,17,13,8,9),
 'lumen':(20,17,11,8,7), 'lux':(18,17,12,8,8),
 'materia':(20,17,12,8,7), 'minty':(19,17,12,8,7),
 'morph':(17,17,12,5,7), 'pulse':(21,17,12,8,7),
 'quartz':(17,17,12,4,6), 'sandstone':(20,17,12,8,7),
 'simplex':(20,17,12,8,7), 'sketchy':(18,17,10,6,4),
 'slate':(20,17,12,6,7), 'solar':(20,17,11,8,8),
 'spacelab':(19,17,12,7,6), 'superhero':(20,17,12,7,7),
 'united':(20,17,12,8,7), 'vapor':(15,17,12,6,4),
 'yeti':(20,17,12,8,6), 'zephyr':(22,18,13,9,8),
}

DESIGN_NOTES = {
 'folio':'The Caslon/green/paper system is distinctive and coherent. The title and H2 consume too much attention; code shrinks on phones. The blue outline button breaks the palette.',
 'atelier':'The rule, teal accents, and sans text form the clearest studio identity. Secondary UI recedes well. The vertical rhythm is loose and mobile code is undersized.',
 'nocturne':'The dark ink surface and selective brass establish a strong hierarchy. The short title rule is a useful accent. Tighten the page rhythm and complete the control palette.',
 'tufte':'A coherent reading page with excellent body scale and a quiet canvas. Italic sections give it a literary voice. This specimen does not exercise Tufte side notes or complex columns.',
 'bootstrap':'The shared SmallDocs structure is clear and the controls are consistent. Its identity remains generic, and the dark outline button needs attention.',
 'cerulean':'Blue headings, links, and controls compete with prose. Gradients add a dated surface treatment without adding useful hierarchy.',
 'cosmo':'Clean hierarchy and crisp controls. The wide Source Sans text block needs a reading-width constraint; primary controls need stronger text contrast.',
 'cyborg':'The black/cyan identity is coherent and prose remains readable. Colored status panels and primary buttons need a contrast pass.',
 'darkly':'A clear dark interface with restrained surfaces. Its colored alert panels and outline button are substantially fainter than the body text.',
 'flatly':'Good flat structure and a confident palette. Teal body links, pastel alerts, and white labels on some colored surfaces need repair.',
 'journal':'Expressive headings create a distinct opening, but body text and controls feel like a separate generic system. Secondary button contrast is weak.',
 'litera':'The strongest editorial direction among the stock options. Paragraphs use Georgia while list items revert to sans; pale alerts and buttons interrupt the otherwise strong reading surface.',
 'lumen':'A calm, familiar UI with modest surface effects. Long lines and low-contrast status messages hold it back.',
 'lux':'The formal palette is coherent. All-cap headings, tracked lowercase text, and light UI weights are too insistent or delicate for sustained documentation.',
 'materia':'Functional hierarchy and a consistent material vocabulary. Bright blue controls and pale colored alerts need stronger foregrounds.',
 'minty':'The mint/coral system is coherent and friendly. Faint body text and white text on pastel controls undermine its usefulness for a reading site.',
 'morph':'The soft blue surfaces and relief are consistent, but the main reading surface lacks separation and contrast. Depth should clarify controls rather than blur their boundaries.',
 'pulse':'A sound purple-accent UI with consistent grouping. Its content surface is conventional, but the sampled controls have strong contrast.',
 'quartz':'The gradient dominates the page and makes foreground contrast vary by location. Glass panels offer little stable separation. Long prose needs a solid reading surface.',
 'sandstone':'An earthy palette gives a quiet identity, but green links and colored status surfaces are too faint. Most layout quality comes from the shared SmallDocs shell.',
 'simplex':'Restrained red accents leave the prose in charge. Buttons have slight gradients, but the sampled foregrounds remain readable. A good low-drama option.',
 'sketchy':'A complete and consistent sketchbook personality. Rough borders and handwritten text suit playful material better than the requested elegant documentation.',
 'slate':'Muted dark surfaces support the content, but embossed gradients add visual weight. Colored status panels need contrast repair.',
 'solar':'An unusually calm dark palette, with little decorative noise. Main text just clears the normal-text threshold; status panels and some buttons do not.',
 'spacelab':'A functional blue/grey UI whose grey prose and gradient controls are too faint. It has little distinctive editorial identity to offset those repairs.',
 'superhero':'A coherent technical blue/orange palette. Body reading is good; bright status panels and white labels on colored buttons are weaker.',
 'united':'Ubuntu and warm orange give the UI a recognizable voice. Primary and secondary controls need darker text/background combinations.',
 'vapor':'The neon identity is coherent, but glow, saturated prose, and colored panels all ask for attention. It fits a playful technology page better than long reading.',
 'yeti':'An unobtrusive sans interface with consistent controls. Blue buttons and body links need stronger contrast; the editorial character is minimal.',
 'zephyr':'The strongest stock general-purpose design here: clear Inter hierarchy, quiet surfaces, coherent controls, and strong sampled contrast. Narrow prose independently of wider controls.',
}

# Original entries retain their first-review editorial awards and observations.
for base in ('folio','atelier','nocturne'):
    FONT[base+'-original'] = FONT[base]
    NOTES[base+'-original'] = NOTES[base]
    DESIGN[base+'-original'] = DESIGN[base]
    DESIGN_NOTES[base+'-original'] = DESIGN_NOTES[base]

# Same criterion weights and anchors, applied to the revised rendered specimens.
DESIGN.update({
 'folio':(23,18,14,9,10), 'atelier':(24,18,14,9,10),
 'nocturne':(24,18,14,9,10),
 'zephyr-reading':(23,19,14,9,8), 'simplex-reading':(22,18,14,9,7),
 'pulse-reading':(23,18,14,9,7), 'litera-reading':(23,18,14,9,9),
 'darkly-reading':(23,18,14,9,8),
})
REFINED_NOTES={
 'folio':'Caslon, paper, and green are retained. Smaller sections and a 640px prose column restore reading priority; code stays 14.45px on phones. The display face is still intentionally expressive.',
 'atelier':'The studio rule and teal palette remain. Tighter prose, restrained headings, and readable phone code make the hierarchy more balanced. A little more space around dense groups may still help.',
 'nocturne':'Ink and brass retain the evening identity. Narrower prose, quieter headings, and theme-aware controls improve continuity; the title still carries deliberate display emphasis.',
 'zephyr-reading':'Inter and the original blue identity remain. The bounded prose column and quieter heading scale improve reading fit, with restrained surfaces and strong normal-state controls.',
 'simplex-reading':'The quiet red identity remains, with flatter controls, bounded prose, and a consistent code face. The system is useful and calm, though less distinctive than the custom designs.',
 'pulse-reading':'Purple remains the visual signature. Smaller headings, bounded prose, and consistent code improve reading priority without adding ornament; the system-font prose stays conventional.',
 'litera-reading':'Georgia now continues through lists. Darker blue links, readable status panels, and a stronger secondary action repair interruptions to the editorial surface. Sans controls retain their separate role.',
 'darkly-reading':'The charcoal and Lato identity remain. Pale blue outline links and muted status panels repair weak text contrast; the narrower prose and larger code improve the reading surface.',
}
for name,note in REFINED_NOTES.items():
    NOTES[name]=('Refined · candidate',note)
    DESIGN_NOTES[name]=note
    if name.endswith('-reading'):
        base=name.removesuffix('-reading')
        FONT[name]=FONT.get(base,(14,'A deliberate, conventional text family with clear emphasis; no stylistic impediment to prose.'))
FONT['litera-reading']=(14,'Georgia is a convincing text face; paragraphs and lists now share the serif voice.')

def design_assess(t):
    controls=json.loads((ROOT/'controls.json').read_text())
    contexts=[]
    for mode in t['modes']:
        r=next(r for r in controls if r['id']==t['id'] and r['mode']==mode['mode'])
        values=[dict(label=c['text'],ratio=contrast_range(c,r)[0],range=contrast_range(c,r)) for c in r['controls']]
        failures=[v for v in values if v['ratio']<4.5]
        metrics=mode['metrics']
        body=4 if metrics['bodyContrast'][0]>=4.5 else 2 if metrics['bodyContrast'][0]>=3 else 0
        ui=4 if not failures else 3 if len(failures)==1 and failures[0]['ratio']>=3 else 2 if len(failures)<=2 else 1 if min(v['ratio'] for v in failures)>=3 else 0
        links=2 if metrics['linkContrast'][0]>=4.5 else 1 if metrics['linkContrast'][0]>=3 else 0
        palette=4 if t['id']=='quartz' else 5
        stable=0 if t['id']=='quartz' else 1 if t['id']=='vapor' else 2
        cues=2 if t['id'] in ['quartz','morph','vapor'] else 3
        points=body+ui+links+palette+stable+cues
        contexts.append(dict(mode=mode['mode'],color=points,controlContrast=values,failures=failures,
            colorParts=dict(body=body,controls=ui,links=links,palette=palette,nonColorCues=cues,stableSurface=stable)))
    h,s,l,su,p=DESIGN[t['id']]
    scores=dict(hierarchy=h,spacing=s,color=min(c['color'] for c in contexts),layout=l,surfaces=su,personality=p)
    return dict(total=sum(scores.values()),scores=scores,contexts=contexts,note=DESIGN_NOTES[t['id']])

def find(id,mode,page,viewport):
    return next(r for r in RAW if (r['id'],r['mode'],r['page'],r['viewportName'])==(id,mode,page,viewport))

def assess(id,mode):
    d,m=(find(id,mode,'typography',v) for v in ['desktop','mobile'])
    dc,mc=(find(id,mode,'code',v) for v in ['desktop','mobile'])
    p=d['paragraphs'][0]; s=p['style']; pm=m['paragraphs'][0]
    size=px(s['fontSize']); leading=px(s['lineHeight'])/size
    mobile_size=px(pm['style']['fontSize'])
    gap=(d['paragraphs'][1]['rect']['top']-p['rect']['bottom'])/size
    mobile_gap=(m['paragraphs'][1]['rect']['top']-pm['rect']['bottom'])/mobile_size
    measure=full_measure(d); mobile_measure=full_measure(m)
    br=contrast_range(p,d,(p['rect']['left'],p['rect']['right']))
    lr=contrast_range(d['link'],d,(p['rect']['left'],p['rect']['right']))
    ir=contrast_range(d['inline'],d,(p['rect']['left'],p['rect']['right']))
    cr=[contrast_range(t,dc) for t in dc['code']['tokens']]
    code_min=min(v[0] for v in cr)
    family,font_reason=FONT.get(id,(14,'A deliberate, conventional text family with clear emphasis; no stylistic impediment to prose.'))
    desktop_measure=measure_score(measure)
    mobile_measure_points=5 if 45<=mobile_measure<=90 else 4 if 35<=mobile_measure<45 else 2 if 30<=mobile_measure<35 else 0
    no_overflow=all(r['documentWidth']<=r['viewport']['width']+1 for r in [d,m,dc,mc])
    if not no_overflow:mobile_measure_points=max(0,mobile_measure_points-2)
    para_points=5 if .5<=gap<=1 and .5<=mobile_gap<=1 else 4 if .4<=gap<=1.3 and .4<=mobile_gap<=1.3 else 2
    if px(s['textIndent'])>0:para_points=max(0,para_points-2)
    gutters=min(pm['rect']['left'],m['viewport']['width']-pm['rect']['right'])
    margin_points=5 if gutters>=15 and no_overflow else 3 if gutters>=10 else 1
    h1,h2,h3=d['headings']; title_ratio=px(h1['style']['fontSize'])/size
    section_ratio=px(h2['style']['fontSize'])/size
    section_points=4 if section_ratio<=1.4 else 3 if section_ratio<=1.8 else 1
    if h2['style']['fontStyle']=='italic':section_points=max(0,section_points-1)
    if h2['style']['textTransform']=='uppercase':section_points=max(0,section_points-2)
    hgap=h3['rect']['top']-d['paragraphs'][1]['rect']['bottom']
    after=m['paragraphs'][0]['rect']['top']-m['headings'][1]['rect']['bottom']
    group_points=3 if hgap>px(h3['style']['marginBottom']) and after>=0 else 1
    title_points=3 if title_ratio<=2 else 2 if title_ratio<=2.8 else 1
    code_size=px(dc['code']['style']['fontSize']); mobile_code=px(mc['code']['style']['fontSize'])
    code_size_points=4 if min(code_size,mobile_code)>=14 else 3 if min(code_size,mobile_code)>=13 else 2 if min(code_size,mobile_code)>=12 else 1
    mono_points=3 if 'mono' in dc['code']['style']['fontFamily'].lower() or 'consolas' in dc['code']['style']['fontFamily'].lower() else 0
    overflow_points=3 if no_overflow and mc['code']['preStyle']['overflowX'] in ['auto','scroll'] else 1
    body_points=4 if br[0]>=4.5 else 2 if br[0]>=3 else 0
    links_points=2 if lr[0]>=4.5 else 1 if lr[0]>=3 else 0
    inline_points=2 if ir[0]>=4.5 else 1 if ir[0]>=3 else 0
    syntax_points=2 if code_min>=4.5 else 1 if code_min>=3 else 0
    scores=dict(font=family,size=10 if min(size,mobile_size)>=15 and max(size,mobile_size)<=25 else 7,
      leading=min(leading_score(leading),leading_score(px(pm['style']['lineHeight'])/mobile_size)),
      measure=desktop_measure+mobile_measure_points,space=para_points+margin_points,
      hierarchy=section_points+group_points+title_points,code=code_size_points+mono_points+overflow_points,
      color=body_points+links_points+inline_points+syntax_points)
    reasons={
      'font':font_reason,
      'size':f'Body {size:g}px desktop / {mobile_size:g}px mobile; preferred range 15–25px.',
      'leading':f'Body leading {leading:.2f}; preferred range 1.20–1.45.',
      'measure':f'Desktop complete-line mean {measure:.1f} characters ({desktop_measure}/10); mobile {mobile_measure:.1f} ({mobile_measure_points}/5, adapted band).',
      'space':f'Paragraph gap {gap:.2f}em desktop / {mobile_gap:.2f}em mobile ({para_points}/5); narrow-screen gutters {gutters:g}px ({margin_points}/5).',
      'hierarchy':f'Section/body ratio {section_ratio:.2f} ({section_points}/4); grouping {group_points}/3; title/body ratio {title_ratio:.2f} ({title_points}/3).',
      'code':f'Code {code_size:g}px desktop / {mobile_code:g}px mobile ({code_size_points}/4); monospace {mono_points}/3; contained scrolling {overflow_points}/3.',
      'color':f'Body {br[0]:.2f}:1 ({body_points}/4); link {lr[0]:.2f}:1 ({links_points}/2); inline code {ir[0]:.2f}:1 ({inline_points}/2); worst sampled syntax {code_min:.2f}:1 ({syntax_points}/2).'
    }
    return dict(mode=mode,total=sum(scores.values()),scores=scores,reasons=reasons,metrics=dict(bodySize=size,mobileBodySize=mobile_size,leading=leading,measure=round(measure,1),mobileMeasure=round(mobile_measure,1),allLineMean=round(all_measure(d),1),bodyContrast=br,linkContrast=lr,inlineContrast=ir,syntaxContrast=round(code_min,3),codeSize=code_size,mobileCodeSize=mobile_code,paragraphGap=round(gap,2),gutter=gutters,overflow=not no_overflow))

def main():
    out=[]
    for t in THEMES:
        modes=[assess(t['id'],mode) for mode in (['light','dark'] if t['paired'] else ['original'])]
        total=min(m['total'] for m in modes)
        item=dict(**t,typography=total,modes=modes,recommendation=NOTES[t['id']][0],note=NOTES[t['id']][1])
        item['design']=design_assess(item)
        out.append(item)
    out.sort(key=lambda t:(-t['typography'],t['name']))
    (ROOT/'scores.json').write_text(json.dumps(out,indent=2))
    for t in out:
        print(t['name'],t['typography'],t['design']['total'],t['design']['scores'])

if __name__=='__main__':main()
