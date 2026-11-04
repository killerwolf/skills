#!/usr/bin/env python3
"""Sound design d'une vidéo courte : bruitages CC0 calés sur l'image, puis mixés sous la voix.

Brouillon d'événements à partir d'une narration (aucun réseau) :
    sound_design.py brouillon --narration narration.json --duree 15 --sortie sfx_events.json

Poser les sons d'une liste d'événements -> une piste de bruitages :
    sound_design.py poser sfx_events.json --sortie sfx.wav [--biblio DOSSIER]

Mixer la piste sous le son d'une vidéo (la voix reste devant) :
    sound_design.py mixer video.mp4 sfx.wav --sortie video_sfx.mp4 [--gain-db -4] [--voix voix.wav]

Mesurer (niveau moyen et crête, par tranche) :
    sound_design.py verifier video_sfx.mp4 [--tranche 2]

Voir la bibliothèque (rôles, variantes, auteurs, licences) :
    sound_design.py biblio [--biblio DOSSIER]

Freesound (clé FREESOUND_API_KEY, réseau vers freesound.org) :
    sound_design.py freesound chercher "whoosh" [--max-duree 1.5] [-n 10]
    sound_design.py freesound prendre 12345 --role whoosh_fast [--biblio DOSSIER]

Fichier d'événements (JSON) :
    {"duree": 15.0, "evenements": [
        {"t": 0.15, "role": "whoosh_fast", "gain": 0.6},
        {"t": 0.20, "role": "pop", "gain": 0.5, "note": "titre"},
        {"t": 4.00, "fichier": "mes_sons/porte.wav", "gain": 0.7}
    ]}
Chaque son est ramené à une crête de -1 dBFS puis multiplié par son gain (0 à 1).
Un rôle avec des variantes (key1.wav, key2.wav…) les alterne. La bibliothèque par défaut est
../assets/sfx (12 sons CC0), ou le dossier donné par --biblio, ou $SOUND_DESIGN_LIB.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ICI = Path(__file__).resolve().parent
BIBLIO_DEFAUT = ICI.parent / 'assets' / 'sfx'
SR = 48000


def biblio_dir(a):
    return Path(a or os.environ.get('SOUND_DESIGN_LIB') or BIBLIO_DEFAUT)


def ffmpeg(args, capture=False):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostdin', *map(str, args)], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit('ffmpeg a échoué :\n' + r.stderr[-1500:])
    return r.stderr


def duree(f):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(f)],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def niveaux(f, debut=None, longueur=None):
    pre = (['-ss', debut] if debut is not None else []) + (['-t', longueur] if longueur is not None else [])
    err = ffmpeg([*pre, '-i', f, '-af', 'volumedetect', '-f', 'null', '-'])
    moy = re.search(r'mean_volume: (-?[\d.]+|-inf) dB', err)
    cre = re.search(r'max_volume: (-?[\d.]+|-inf) dB', err)
    v = lambda m: float(m.group(1)) if m and m.group(1) != '-inf' else -99.0
    return v(moy), v(cre)


def roles(lib):
    """{rôle: [fichiers]} ; key1.wav, key2.wav… -> rôle « key »."""
    out = {}
    for f in sorted(lib.glob('*.wav')):
        out.setdefault(re.sub(r'\d+$', '', f.stem), []).append(f)
    return out


# ---------------------------------------------------------------- brouillon
def brouillon(a):
    nar = json.load(open(a.narration))
    lignes = nar['lines'] if isinstance(nar, dict) else nar
    ev = []
    for k, l in enumerate(lignes):
        t = float(l.get('t', l.get('start', 0)))
        txt = l.get('text', '')
        if k == 0:
            ev.append({'t': round(max(0, t - 0.15), 2), 'role': 'whoosh_fast', 'gain': 0.6, 'note': 'accroche'})
            ev.append({'t': round(t + 0.05, 2), 'role': 'impact_light', 'gain': 0.55, 'note': txt[:40]})
        else:
            ev.append({'t': round(max(0, t - 0.12), 2), 'role': 'whoosh_soft', 'gain': 0.45, 'note': 'transition'})
            ev.append({'t': round(t + 0.02, 2), 'role': 'pop', 'gain': 0.4, 'note': txt[:40]})
        if re.search(r'\d', txt) and k > 0:
            ev.append({'t': round(t + 0.6, 2), 'role': 'impact', 'gain': 0.5, 'note': 'chiffre à vérifier'})
    if lignes:
        last = float(lignes[-1].get('t', lignes[-1].get('start', 0)))
        ev.append({'t': round(last + 0.3, 2), 'role': 'ding', 'gain': 0.5, 'note': 'fin / appel à l\'action'})
    out = {'duree': a.duree, 'evenements': ev,
           '_a_faire': "Brouillon : recale chaque t sur l'image (apparition réelle du texte), retire ce qui surcharge, "
                       "ajoute les transitions et les frappes. Ensuite : poser."}
    json.dump(out, open(a.sortie, 'w'), ensure_ascii=False, indent=1)
    print(f'{a.sortie} : {len(ev)} événements proposés (à recaler sur l\'image)')


# ---------------------------------------------------------------- poser
def poser(a):
    spec = json.load(open(a.evenements))
    D = float(a.duree or spec.get('duree') or 0)
    if D <= 0:
        sys.exit('durée inconnue : mets "duree" dans le fichier ou passe --duree')
    lib = biblio_dir(a.biblio)
    R = roles(lib)
    base = Path(a.evenements).resolve().parent
    crete, inputs, fc, poses, manque = {}, [], [], [], []
    compteur = {}
    for e in sorted(spec['evenements'], key=lambda e: e['t']):
        if 'fichier' in e:
            f = Path(e['fichier']); f = f if f.is_absolute() else base / f
        else:
            var = R.get(e['role'])
            if not var:
                manque.append(e.get('role')); continue
            n = compteur.get(e['role'], 0); compteur[e['role']] = n + 1
            f = var[n % len(var)]
        if not f.exists():
            manque.append(str(f)); continue
        if f not in crete:
            crete[f] = niveaux(f)[1]
        g = float(e.get('gain', 0.6)) * 10 ** ((-1 - crete[f]) / 20)
        i = len(poses); ms = int(round(float(e['t']) * 1000))
        inputs += ['-i', f]
        coupe = f"atrim=0:{e['coupe']},afade=t=out:st={max(0, e['coupe'] - 0.15):.2f}:d=0.15," if 'coupe' in e else ''
        fc.append(f'[{i}:a]aformat=sample_rates={SR}:channel_layouts=stereo,{coupe}adelay={ms}|{ms},volume={g:.4f},apad,atrim=0:{D}[s{i}]')
        poses.append(e)
    if not poses:
        sys.exit('aucun son posé (rôles manquants : ' + ', '.join(sorted(set(map(str, manque)))) + ')')
    fc.append(''.join(f'[s{i}]' for i in range(len(poses))) +
              f'amix=inputs={len(poses)}:duration=longest:normalize=0,alimiter=limit=0.89:level=disabled[o]')
    # au-delà de ~200 entrées, ffmpeg reste correct mais lent : regrouper si besoin
    ffmpeg(['-y', '-loglevel', 'error', *inputs, '-filter_complex', ';'.join(fc), '-map', '[o]', '-t', D, '-ar', SR, a.sortie])
    moy, cre = niveaux(a.sortie)
    print(f'{a.sortie} : {len(poses)} sons posés, moyenne {moy} dB, crête {cre} dB')
    if manque:
        print('Ignorés (rôle ou fichier absent) : ' + ', '.join(sorted(set(map(str, manque)))))


# ---------------------------------------------------------------- mixer
def mixer(a):
    D = duree(a.video)
    g = 10 ** (a.gain_db / 20)
    inputs = ['-i', a.video, '-i', a.sfx] + (['-i', a.voix] if a.voix else [])
    if a.voix:   # les bruitages s'effacent (≈ -6 dB) quand la voix parle
        fc = (f'[1:a]aformat=sample_rates={SR}:channel_layouts=stereo,volume={g:.4f}[s];'
              f'[2:a]aformat=sample_rates={SR}:channel_layouts=stereo[vk];'
              f'[s][vk]sidechaincompress=threshold=0.03:ratio=3:attack=10:release=250[sd];'
              f'[0:a]aformat=sample_rates={SR}:channel_layouts=stereo[o];'
              f'[o][sd]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89:level=disabled[a]')
    else:
        fc = (f'[0:a]aformat=sample_rates={SR}:channel_layouts=stereo[o];'
              f'[1:a]aformat=sample_rates={SR}:channel_layouts=stereo,volume={g:.4f}[s];'
              f'[o][s]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89:level=disabled[a]')
    ffmpeg(['-y', '-loglevel', 'error', *inputs, '-filter_complex', fc, '-map', '0:v', '-map', '[a]',
            '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', D, '-movflags', '+faststart', a.sortie])
    moy, cre = niveaux(a.sortie)
    print(f'{a.sortie} : moyenne {moy} dB, crête {cre} dB')


# ---------------------------------------------------------------- verifier
def verifier(a):
    D = duree(a.fichier)
    moy, cre = niveaux(a.fichier)
    print(f'{a.fichier} : {D:.1f} s, moyenne {moy} dB, crête {cre} dB' + ('  <- SATURE' if cre > -0.5 else ''))
    t = 0.0
    while t < D - 0.05:
        m, c = niveaux(a.fichier, round(t, 2), a.tranche)
        barre = '#' * max(0, int((m + 40) / 1.5))
        print(f'  {t:6.1f} s  moy {m:6.1f}  crête {c:6.1f}  {barre}')
        t += a.tranche


# ---------------------------------------------------------------- biblio
def biblio(a):
    lib = biblio_dir(a.biblio)
    cred = json.load(open(lib / 'credits.json')) if (lib / 'credits.json').exists() else {}
    cred = {c['file']: c for c in (cred if isinstance(cred, list) else cred.values())} if cred else {}
    print(f'Bibliothèque : {lib}')
    for r, fs in roles(lib).items():
        for f in fs:
            c = cred.get(f.name, {})
            print(f"  {r:<13} {f.name:<18} {duree(f):5.2f} s  {c.get('license', '?'):<5} {c.get('author', '?')}  {c.get('page_url', '')}")


# ---------------------------------------------------------------- freesound
API = 'https://freesound.org/apiv2'
CHAMPS = 'id,name,username,license,duration,previews,url,avg_rating,num_downloads'


def fs_appel(chemin, **p):
    cle = os.environ.get('FREESOUND_API_KEY')
    if not cle:
        sys.exit('FREESOUND_API_KEY absente : clé gratuite sur https://freesound.org/apiv2/apply')
    p['token'] = cle
    req = urllib.request.Request(f'{API}{chemin}?{urllib.parse.urlencode(p)}', headers={'User-Agent': 'sound-design-skill/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404 and chemin == '/search/':     # anciennes versions de l'API : /search/text/
            return fs_appel('/search/text/', **{k: v for k, v in p.items() if k != 'token'})
        sys.exit(f'Freesound : HTTP {e.code}. 401 = clé refusée ; 403 sans corps = réseau bloqué (proxy ou IP de datacenter).')


def freesound(a):
    if a.action == 'chercher':
        filtre = 'license:"Creative Commons 0"' + (f' duration:[0 TO {a.max_duree}]' if a.max_duree else '')
        res = fs_appel('/search/', query=a.requete, filter=filtre, fields=CHAMPS, page_size=a.n, sort='rating_desc')
        for s in res['results']:
            print(f"{s['id']:>8}  {s['duration']:5.2f} s  ★{s.get('avg_rating', 0):.1f}  {s['name'][:50]:<50} {s['username']}")
    else:
        s = fs_appel(f'/sounds/{a.requete}/', fields=CHAMPS)
        if 'Creative Commons 0' not in s['license'] and '/zero/' not in s['license']:
            sys.exit(f"Licence {s['license']} : pas CC0, non ajouté.")
        lib = biblio_dir(a.biblio); lib.mkdir(parents=True, exist_ok=True)
        dst = lib / f'{a.role}.wav'
        if dst.exists():
            sys.exit(f'{dst} existe déjà : choisis un autre nom de rôle (ex. {a.role}2).')
        tmp = lib / f'.fs{s["id"]}.mp3'
        with urllib.request.urlopen(urllib.request.Request(s['previews']['preview-hq-mp3'], headers={'User-Agent': 'sound-design-skill/1.0'}), timeout=60) as r:
            tmp.write_bytes(r.read())
        ffmpeg(['-y', '-loglevel', 'error', '-i', tmp, '-af', 'silenceremove=start_periods=1:start_threshold=-50dB',
                '-ar', SR, '-ac', 2, '-c:a', 'pcm_s16le', dst])
        tmp.unlink()
        ajouter_credit(lib, dst.name, re.sub(r'\d+$', '', a.role), 'Freesound', s['username'], 'CC0', s['url'], s['name'])
        print(f'{dst} ({duree(dst):.2f} s) ajouté, crédit noté')


def ajouter_credit(lib, fichier, role, source, auteur, licence, url, original):
    p = lib / 'credits.json'
    c = json.load(open(p)) if p.exists() else {}
    if isinstance(c, list):
        c = {x['file']: x for x in c}
    c[fichier] = {'file': fichier, 'role': role, 'source_pack': source, 'author': auteur,
                  'license': licence, 'page_url': url, 'original_filename': original}
    json.dump(c, open(p, 'w'), ensure_ascii=False, indent=2)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest='cmd', required=True)
    b = s.add_parser('brouillon'); b.add_argument('--narration', required=True); b.add_argument('--duree', type=float, required=True)
    b.add_argument('--sortie', default='sfx_events.json')
    po = s.add_parser('poser'); po.add_argument('evenements'); po.add_argument('--sortie', default='sfx.wav')
    po.add_argument('--duree', type=float); po.add_argument('--biblio')
    m = s.add_parser('mixer'); m.add_argument('video'); m.add_argument('sfx'); m.add_argument('--sortie', required=True)
    m.add_argument('--gain-db', type=float, default=-4.0); m.add_argument('--voix')
    v = s.add_parser('verifier'); v.add_argument('fichier'); v.add_argument('--tranche', type=float, default=2.0)
    bi = s.add_parser('biblio'); bi.add_argument('--biblio')
    f = s.add_parser('freesound'); f.add_argument('action', choices=['chercher', 'prendre']); f.add_argument('requete')
    f.add_argument('--max-duree', type=float); f.add_argument('-n', type=int, default=10); f.add_argument('--role')
    f.add_argument('--biblio')
    a = p.parse_args()
    if a.cmd == 'freesound' and a.action == 'prendre' and not a.role:
        p.error('freesound prendre : --role est obligatoire')
    {'brouillon': brouillon, 'poser': poser, 'mixer': mixer, 'verifier': verifier, 'biblio': biblio, 'freesound': freesound}[a.cmd](a)


if __name__ == '__main__':
    try:
        main()
    except BrokenPipeError:      # sortie coupée par | head : sans erreur
        sys.exit(0)
