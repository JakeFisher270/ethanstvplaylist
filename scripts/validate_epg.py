#!/usr/bin/env python3
"""Never publish a blank, malformed, or out-of-date guide."""
import datetime, pathlib, sys, xml.etree.ElementTree as ET
source, target = map(pathlib.Path, sys.argv[1:3])
if not source.exists() or source.stat().st_size < 100:
    raise SystemExit('EPG download empty; keeping old guide')
root = ET.parse(source).getroot()
if root.tag != 'tv':
    raise SystemExit('Invalid XMLTV document')
programmes = root.findall('programme')
if not programmes:
    raise SystemExit('No programs; keeping old guide')
now = datetime.datetime.now(datetime.timezone.utc)
recent = 0
for item in programmes:
    try:
        start = datetime.datetime.strptime(item.attrib['start'][:14], '%Y%m%d%H%M%S').replace(tzinfo=datetime.timezone.utc)
        if abs((start-now).total_seconds()) < 72*3600:
            recent += 1
    except (KeyError, ValueError):
        pass
if not recent:
    raise SystemExit('Guide contains no current schedule; keeping old guide')
source.replace(target)
print(f'Published {len(programmes)} programs ({recent} near current date)')
