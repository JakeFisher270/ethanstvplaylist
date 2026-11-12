#!/usr/bin/env python3
"""Build a curated, English-language M3U from IPTV-org's public English playlist."""
import re, urllib.request, pathlib, collections
SOURCE='https://iptv-org.github.io/iptv/languages/eng.m3u'
OUT=pathlib.Path(__file__).resolve().parents[1]/'EthansTV-combined.m3u'
EPG='https://raw.githubusercontent.com/JakeFisher270/ethanstvplaylist/main/guide.xml'
CATEGORY_MAP={
 'sports':'Sports','news':'News','movies':'Movies','entertainment':'Entertainment',
 'series':'Series','kids':'Kids','animation':'Kids','documentary':'Documentary',
 'science':'Documentary','education':'Documentary','lifestyle':'Lifestyle',
 'cooking':'Lifestyle','travel':'Lifestyle','music':'Music','comedy':'Entertainment',
 'classic':'Movies','family':'Entertainment','business':'News','weather':'News',
 'general':'Entertainment','culture':'International','outdoor':'Lifestyle',
 'auto':'Lifestyle','relax':'Lifestyle','shop':'Lifestyle',
}
ORDER=['US Local TV','Sports','News','Movies','Entertainment','Series','Kids','Documentary','Lifestyle','Music','International']
attrs=re.compile(r'([\w-]+)="([^"]*)"')
def get_text(url):
 req=urllib.request.Request(url,headers={'User-Agent':'EStreamsPlaylistBuilder/1.0'})
 with urllib.request.urlopen(req,timeout=60) as r:return r.read().decode('utf-8-sig')
def main():
 lines=get_text(SOURCE).splitlines()
 groups=collections.defaultdict(list); seen=set(); count=0
 for i,line in enumerate(lines):
  if not line.startswith('#EXTINF:'):continue
  if i+1>=len(lines):continue
  stream=lines[i+1].strip()
  if not stream.startswith(('http://','https://')):continue
  meta=dict(attrs.findall(line))
  name=line.rsplit(',',1)[-1].strip()
  if not name:continue
  tvgid=meta.get('tvg-id','').strip()
  key=(tvgid or name.casefold(),stream)
  if key in seen:continue
  seen.add(key)
  old=meta.get('group-title','').strip().lower()
  country=tvgid.split('.')[-1].split('@')[0].lower() if '.' in tvgid else ''
  if country=='us' and ('local' in name.lower() or re.search(r'\b(?:ABC|CBS|NBC|FOX|PBS|CW)\b',name,re.I)):
   group='US Local TV'
  elif old in CATEGORY_MAP:group=CATEGORY_MAP[old]
  elif country and country not in ('us','ca'):group='International'
  else:group='Entertainment'
  # Keep the canonical tvg-id unchanged for XMLTV matching.
  def esc(s):return s.replace('"',"'").replace('\r',' ').replace('\n',' ')
  props=' '.join(f'{k}="{esc(meta[k])}"' for k in ('tvg-id','tvg-logo','tvg-country','tvg-language') if meta.get(k))
  entry=f'#EXTINF:-1 {props} group-title="{group}",{name}\r\n{stream}\r\n'
  groups[group].append((name.casefold(),entry));count+=1
 with OUT.open('w',encoding='utf-8',newline='') as f:
  f.write(f'#EXTM3U x-tvg-url="{EPG}"\r\n')
  for group in ORDER:
   for _,entry in sorted(groups[group]):f.write(entry)
 print('Wrote',OUT,'with',count,'channels')
 for group in ORDER:print(group,len(groups[group]))
if __name__=='__main__':main()
