from pathlib import Path
import re, subprocess, struct

root = Path(__file__).resolve().parents[1]
voice = root / 'voiceover'
thumbs = root / 'thumbnails'
voice.mkdir(exist_ok=True)
thumbs.mkdir(exist_ok=True)
text = (root / 'script.md').read_text()
name_map = {'1':'01_hook','2':'02_register_and_authenticate','3':'03_upload_without_a_browser','4':'04_the_response_is_machine-usable','5':'05_it_is_more_than_upload','6':'06_why_this_matters'}
for m in re.finditer(r'^## (\d+) — ([^\n]+)\n\n(.*?)(?=^## |\Z)', text, flags=re.M|re.S):
    num, _title, body = m.groups()
    if num not in name_map: continue
    body = re.sub(r'\[S\d+\]', '', body)
    body = re.sub(r'`([^`]+)`', r'\1', body)
    body = re.sub(r'\*\*([^*]+)\*\*', r'\1', body)
    body = re.sub(r'\n+', ' ', body).strip()
    wav = voice / f'{name_map[num]}.wav'; mp3 = voice / f'{name_map[num]}.mp3'
    subprocess.run(['espeak','-v','en-us','-s','150','-w',str(wav),body], check=True)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(wav),'-ac','1','-ar','22050','-codec:a','libmp3lame','-b:a','24k',str(mp3)], check=True)
    wav.unlink()
for src in sorted((root/'thumbnails_src').glob('*.svg')):
    subprocess.run(['rsvg-convert','-w','1280','-h','720','-o',str(thumbs/(src.stem+'.png')),str(src)], check=True)
def png_size(path):
    data=path.read_bytes()[:24]
    if data[:8] != b'\x89PNG\r\n\x1a\n': raise ValueError(path)
    return struct.unpack('>II',data[16:24])
def duration(path):
    return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(path)],text=True).strip())
mp3s=sorted(voice.glob('*.mp3')); svgs=sorted((root/'visuals').glob('*.svg')); pngs=sorted(thumbs.glob('*.png')); errors=[]
if len(mp3s)!=6: errors.append(f'expected 6 voiceovers, got {len(mp3s)}')
if len(svgs)!=11: errors.append(f'expected 11 visuals, got {len(svgs)}')
if len(pngs)!=3: errors.append(f'expected 3 thumbnails, got {len(pngs)}')
for p in svgs:
    s=p.read_text()
    if 'width="1920"' not in s or 'height="1080"' not in s: errors.append(f'visual dimensions invalid: {p.name}')
for p in pngs:
    if png_size(p)!=(1280,720): errors.append(f'thumbnail dimensions invalid: {p.name}')
words=len(re.findall(r"\b[\w’'-]+\b",re.sub(r'\[S\d+\]','',text))); total=sum(duration(p) for p in mp3s)
validation='\n'.join([f'script_words={words}',f'voiceover_sections={len(mp3s)}',f'voiceover_duration_seconds={total:.2f}',f'visuals={len(svgs)} at 1920x1080 SVG',f'thumbnails={len(pngs)} at 1280x720 PNG',f'errors={len(errors)}']+[f'ERROR: {e}' for e in errors])+'\n'
(root/'validation.txt').write_text(validation); print(validation,end='')
if errors: raise SystemExit(1)
