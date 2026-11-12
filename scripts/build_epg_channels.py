#!/usr/bin/env python3
"""Select supported English guide mappings for playlist channel IDs."""
import pathlib, re, sys, xml.etree.ElementTree as ET
root = pathlib.Path(__file__).resolve().parents[1]
playlist = root / 'EthansTV-combined.m3u'
if not playlist.exists():
    playlist = root / 'app/src/main/assets/channels.m3u'
ids = set(re.findall(r'tvg-id="([^"@]+)(?:@[^"]*)?"', playlist.read_text(encoding='utf-8')))
# Keep guide requests bounded so scheduled Actions do not run indefinitely.
MAX_CHANNELS = 250
choices = {}
for file in pathlib.Path(sys.argv[1], 'sites').rglob('*.channels.xml'):
    try:
        tree = ET.parse(file)
    except ET.ParseError:
        continue
    for node in tree.iter('channel'):
        cid = node.get('xmltv_id', '').split('@')[0]
        lang = node.get('lang', '')
        if cid not in ids or not node.get('site_id') or not node.get('site'):
            continue
        if lang != 'en' and not lang.startswith('en-'):
            continue
        if cid not in choices:
            choices[cid] = dict(node.attrib)
            choices[cid]['xmltv_id'] = node.get('xmltv_id', cid)
channels = ET.Element('channels')
for cid in sorted(choices)[:MAX_CHANNELS]:
    ET.SubElement(channels, 'channel', choices[cid]).text = cid
ET.ElementTree(channels).write(root / 'epg.channels.xml', encoding='utf-8', xml_declaration=True)
print(f'Mapped {len(channels)} of {len(ids)} unique playlist IDs to guide sources')
if not len(channels):
    raise SystemExit('No EPG source matches; not overwriting guide')
