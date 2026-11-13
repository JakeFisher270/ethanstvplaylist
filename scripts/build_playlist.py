#!/usr/bin/env python3
"""Build E Streams playlist from current iptv-org public feeds; not a license audit."""
import re, urllib.request, pathlib, html
ROOT=pathlib.Path(__file__).resolve().parent
SOURCES=[('Kentucky','https://iptv-org.github.io/iptv/subdivisions/us-ky.m3u'),('United States','https://iptv-org.github.io/iptv/countries/us.m3u'),('English','https://iptv-org.github.io/iptv/languages/eng.m3u')]
CATEGORIES=[('Kentucky News',r'(?i)\b(kentucky|lexington|louisville|wkyt|wlex|wdrb|wave|whas|wymt|wku|ket|fox 56|abc 36|wltx)\b'),('US News',r'(?i)news|weather|local|abc|cbs|nbc|fox|pbs|scripps|newsy|bloomberg|reuters|associated press'),('Sports',r'(?i)sports?|espn|golf|racing|football|basketball|soccer|tennis|fight'),('Movies Live',r'(?i)movies?|cinema|film|classic'),('Series Live',r'(?i)series|drama|sitcom|comedy'),('Documentaries',r'(?i)documentary|science|history|nature|education'),('Kids & Family',r'(?i)kids|children|family|animation|cartoon'),('Entertainment',r'(?i)entertainment|general|lifestyle|music|cooking|travel')]
ATTR=re.compile(r'([\w-]+)="([^"]*)"')
def parse(text):
 lines=text.replace('\r','').split('\n'); out=[]
 for i,line in enumerate(lines):
  if not line.startswith('#EXTINF:'):continue
  url=next((s.strip() for s in lines[i+1:] if s.strip() and not s.startswith('#')),None)
  if not url or not url.startswith(('http://','https://')):continue
  meta=line.split(',',1); name=meta[1].strip() if len(meta)>1 else 'Unnamed'
  attrs=dict(ATTR.findall(meta[0])); out.append((name,url,attrs))
 return out
def classify(name,attrs,ky=False):
 value=name+' '+attrs.get('group-title','')
 if ky or CATEGORIES[0][1].search(value):return 'Kentucky News' if re.search(r'(?i)news|wkyt|wlex|wdrb|wave|whas|wymt|fox|abc|nbc|cbs|pbs|ket',value) else 'Kentucky Local'
 for group,regex in CATEGORIES[1:]:
  if regex.search(value):return group
 return 'Other Live TV'
def main():
 entries={}; results=[]
 for label,url in SOURCES:
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'EStreamsPlaylistBuilder/2.0'})
   with urllib.request.urlopen(req,timeout=35) as response: data=response.read().decode('utf-8-sig','replace')
   parsed=parse(data);results.append(f'{label}: {len(parsed)} source entries')
   for name,stream,attrs in parsed:
    key=attrs.get('tvg-id') or stream
    if key in entries:continue
    # English feed can include global channels; keep all explicitly English-language source entries.
    entries[key]=(name,stream,attrs,classify(name,attrs,label=='Kentucky'))
  except Exception as exc:results.append(f'{label}: FAILED {exc}')
 if not entries:raise RuntimeError('All upstream sources failed; existing playlist not overwritten')
 order=['Kentucky News','Kentucky Local','US News','Sports','Movies Live','Series Live','Documentaries','Kids & Family','Entertainment','Other Live TV']
 with (ROOT/'EthansTV-combined.m3u').open('w',encoding='utf-8',newline='\n') as out:
  out.write('#EXTM3U x-tvg-url="https://raw.githubusercontent.com/JakeFisher270/ethanstvplaylist/main/guide.xml"\n')
  for name,stream,attrs,group in sorted(entries.values(),key=lambda e:(order.index(e[3]),e[0].lower())):
   a=' '.join(f'{k}="{html.escape(v,quote=True)}"' for k,v in attrs.items() if k not in ('group-title',) and v)
   out.write(f'#EXTINF:-1 {a} group-title="{group}",{name}\n{stream}\n')
 print('\n'.join(results));print('Unique channels:',len(entries))
if __name__=='__main__':main()
