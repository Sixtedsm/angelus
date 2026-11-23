"""Enregistre l'Évangile du jour (AELF) avec une voix neuronale, pour aujourd'hui et les 7 jours suivants.

Usage : python tools/evangile.py audio/evangile
Lancé chaque nuit par GitHub (.github/workflows/site.yml). Voix : edge-tts, gratuite, sans clé.
"""
import asyncio, datetime, html, json, pathlib, re, sys, urllib.request
import edge_tts

VOICE, RATE, PITCH = 'fr-FR-HenriNeural', '-10%', '-3Hz'  # voix d'homme posée ; ralentie et un peu plus grave


def gospel_text(date):
    req = urllib.request.Request(f'https://api.aelf.org/v1/messes/{date}/france', headers={'User-Agent': 'angelus-reveil'})
    j = json.load(urllib.request.urlopen(req, timeout=30))
    messe = next((m for m in j['messes'] if re.search('du jour', m.get('nom', ''), re.I)), j['messes'][0])
    ev = next(l for l in messe['lectures'] if l['type'] == 'evangile')
    body = re.sub(r'<br\s*/?>', ' ', ev['contenu'])
    body = re.sub(r'</p>', '\n\n', body)
    body = html.unescape(re.sub(r'<[^>]+>', '', body))
    paras = [re.sub(r'\s+', ' ', p).strip() for p in body.split('\n\n')]
    intro = (ev.get('intro_lue') or 'Évangile de Jésus Christ').rstrip('.') + '.'
    return '\n\n'.join([intro, *[p for p in paras if p], 'Acclamons la Parole de Dieu.'])


async def main(out):
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=1))).date()  # heure de Paris (hiver)
    for i in range(8):
        date = (today + datetime.timedelta(days=i)).isoformat()
        try:
            await edge_tts.Communicate(gospel_text(date), VOICE, rate=RATE, pitch=PITCH).save(str(out / f'{date}.mp3'))
            print('ok', date)
        except Exception as e:  # un jour manquant ne bloque pas les autres ; l'app retombe sur la voix du téléphone
            print('ÉCHEC', date, e)


if __name__ == '__main__':
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'audio/evangile'))
