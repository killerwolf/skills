#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10,<3.15"
# dependencies = ["google-genai>=2.34", "numpy"]
# ///
"""Voix avec Gemini pour une vidéo : une voix, un dialogue à deux voix, ou la découpe d'un dialogue.

Une voix :
    gemini_voix.py voix --voix Algenib --style "vieil homme bourru" \
        --texte "C'est qui, là dehors ?" --sortie audio/05_portier.mp3

Un dialogue à deux voix, en un seul appel :
    gemini_voix.py dialogue dialogue.txt --sortie audio/dialogue.mp3

Découper un dialogue déjà généré en une réplique par fichier (aucun appel) :
    gemini_voix.py decouper dialogue.txt audio/dialogue.mp3 --debut 1

Fichier de dialogue : d'abord les voix, puis une réplique par ligne (personnage | style | texte) :
    @Portier = Algenib
    @Voyageur = Puck
    Portier | vieil homme bourru | C'est qui, là dehors ?
    Voyageur | jeune bourgeois outré | Pardon ?

--simuler montre ce qui serait envoyé, sans appel. Un appel n'est jamais relancé tout seul.
La clé est lue dans GEMINI_API_KEY, sinon dans le .env du dossier courant ou d'un dossier parent.
Elle n'est jamais affichée.
"""
import argparse
import base64
import os
import re
import subprocess
import wave
from pathlib import Path

import numpy as np

MODELE = "gemini-3.8-flash-tts"
PCM_SR = 24000  # format de Gemini : mono, 16 bits, 24 kHz
SR = 44100
FEN = 0.01


def lire_cle():
    cle = os.environ.get("GEMINI_API_KEY", "")
    if not cle:
        for dossier in [Path.cwd(), *Path.cwd().parents]:
            env = dossier / ".env"
            if env.is_file():
                for ligne in env.read_text(encoding="utf-8").splitlines():
                    if ligne.startswith("GEMINI_API_KEY="):
                        cle = ligne.split("=", 1)[1].strip().strip("\"'")
            if cle:
                break
    if not cle:
        raise SystemExit("Clé absente : colle ta clé Google AI Studio après GEMINI_API_KEY= dans le fichier .env du projet, puis relance.")
    return cle


def verifier_texte(texte):
    """Gemini lit le texte tel quel : des balises entre crochets seraient dites à voix haute."""
    if re.search(r"\[[^\]]*\]", texte):
        raise SystemExit(f"Balise entre crochets refusée : « {texte} ». Mets le ton dans le style ; rires et soupirs : <laugh>, <sigh>.")


def lire_dialogue(chemin):
    voix, tours = {}, []
    for ligne in Path(chemin).read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#"):
            continue
        if ligne.startswith("@"):
            nom, v = ligne[1:].split("=", 1)
            voix[nom.strip()] = v.strip()
        else:
            parties = [p.strip() for p in ligne.split("|")]
            if len(parties) != 3:
                raise SystemExit(f"Ligne à corriger (personnage | style | texte) : {ligne}")
            verifier_texte(parties[2])
            tours.append(parties)
    if len(voix) != 2:
        raise SystemExit(f"Il faut exactement 2 voix (limite de Gemini), trouvé : {len(voix)}.")
    inconnus = {t[0] for t in tours} - set(voix)
    if inconnus or not tours:
        raise SystemExit(f"Personnage sans voix ou dialogue vide : {sorted(inconnus)}")
    return voix, tours


def appeler(modele, contenu, speech_config):
    """Un seul appel. Le SDK relance tout seul sur 429 et 5xx : attempts=0 ne suffit pas (il le remet à 1),
    donc on ne lui laisse relancer qu'un code qui n'existe pas (599). Reste une relance si la connexion coupe."""
    from google import genai

    cle = lire_cle()
    print(f"Appels à l'API prévus : 1 (modèle {modele}).", flush=True)
    client = genai.Client(api_key=cle, http_options={"retry_options": {"attempts": 0, "http_status_codes": [599]}})
    try:
        reponse = client.interactions.create(
            model=modele,
            input=[{"type": "user_input", "content": contenu}],
            response_format={"type": "audio"},
            generation_config={"speech_config": speech_config},
        )
    except Exception as e:  # le SDK a plusieurs familles d'erreurs, selon la partie appelée
        code = getattr(e, "status_code", None) or getattr(e, "code", None)
        if code == 429 or "RESOURCE_EXHAUSTED" in str(e):
            raise SystemExit("Quota Gemini épuisé (RESOURCE_EXHAUSTED) : aucune relance. "
                             "Le quota du jour revient à minuit heure du Pacifique. "
                             "Les chiffres exacts sont dans Google AI Studio.")
        raise SystemExit(f"Erreur Gemini {code or type(e).__name__} : {e}. Aucune relance.")
    audio = getattr(reponse, "output_audio", None)
    if audio is None or not audio.data:
        raise SystemExit(f"Gemini n'a pas renvoyé d'audio (état : {getattr(reponse, 'status', '?')}). Aucune relance.")
    return base64.b64decode(audio.data)


def lire_audio(chemin):
    brut = subprocess.run(["ffmpeg", "-v", "error", "-i", str(chemin), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                          capture_output=True, check=True).stdout
    return np.frombuffer(brut, np.float32).copy()


def ecrire_audio_brut(chemin, x):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", str(chemin)],
                   input=x.astype(np.float32).tobytes(), check=True)


def ecrire_audio(donnees, sortie):
    """Garde le .wav d'origine à côté, puis convertit en MP3 mono, 44,1 kHz, 128 kb/s."""
    wav = sortie.with_suffix(".wav")
    if donnees[:4] == b"RIFF":
        wav.write_bytes(donnees)
    else:  # PCM sans en-tête
        with wave.open(str(wav), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(PCM_SR)
            w.writeframes(donnees)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-ac", "1", "-ar", str(SR),
                    "-codec:a", "libmp3lame", "-b:a", "128k", str(sortie)], check=True)
    mesurer(sortie)


def lufs(x):
    r = subprocess.run(["ffmpeg", "-nostats", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", "ebur128", "-f", "null", "-"],
                       input=x.astype(np.float32).tobytes(), capture_output=True).stderr.decode()
    return float(r[r.rfind("I:") + 2:].split()[0])


def mesurer(f):
    x = lire_audio(f)
    print(f"{f.name} : durée {len(x) / SR:.2f} s, sonie {lufs(x):.1f} LUFS")


def verifier_sortie(sortie):
    if sortie.exists() or sortie.with_suffix(".wav").exists():
        raise SystemExit(f"{sortie} existe déjà : on n'écrase rien. Choisis un autre nom.")
    sortie.parent.mkdir(parents=True, exist_ok=True)


def cmd_voix(a):
    texte = a.texte if a.texte else Path(a.fichier).read_text(encoding="utf-8").strip()
    verifier_texte(texte)
    sortie = Path(a.sortie)
    verifier_sortie(sortie)
    tour = {"type": "text", "text": texte}
    if a.style:
        tour["annotations"] = [{"type": "speech_metadata", "style": a.style}]
    if a.simuler:
        print(f"Simulation, aucun appel. Voix {a.voix}, modèle {a.modele}\n{tour}")
        return
    ecrire_audio(appeler(a.modele, [tour], [{"voice": a.voix}]), sortie)


def cmd_dialogue(a):
    voix, tours = lire_dialogue(a.fichier)
    sortie = Path(a.sortie)
    verifier_sortie(sortie)
    contenu = [{"type": "text", "text": texte + " <long pause>\n",  # la pause rend la découpe plus sûre, le montage la rogne
                "annotations": [{"type": "speech_metadata", "speaker": qui, "style": style}]}
               for qui, style, texte in tours]
    if a.simuler:
        print(f"Simulation, aucun appel. Voix {voix}, modèle {a.modele}, {len(tours)} répliques")
        for c in contenu:
            print(c["annotations"][0]["speaker"], "|", c["annotations"][0]["style"], "|", c["text"].strip())
        return
    config = {"speakers": [{"speaker": qui, "voice": v} for qui, v in voix.items()]}
    ecrire_audio(appeler(a.modele, contenu, config), sortie)


def niveaux(x):
    w = int(FEN * SR)
    n = len(x) // w
    e = np.sqrt((x[: n * w].reshape(n, w) ** 2).mean(1) + 1e-12)
    return 20 * np.log10(e)


def silences(db, seuil, duree_min):
    """Liste des (début, fin) en secondes des silences sous `seuil` dB d'au moins `duree_min` s."""
    bas = db < seuil
    out, debut = [], None
    for i, b in enumerate(np.append(bas, False)):
        if b and debut is None:
            debut = i
        elif not b and debut is not None:
            if (i - debut) * FEN >= duree_min:
                out.append((debut * FEN, i * FEN))
            debut = None
    return out


def fondu(seg, ms=8):
    k = int(SR * ms / 1000)
    if len(seg) > 2 * k:
        r = np.linspace(0, 1, k, dtype=np.float32)
        seg[:k] *= r
        seg[-k:] *= r[::-1]
    return seg


def couper_aux_silences(x, n):
    """Coupe aux n−1 silences les plus longs : ceux entre deux tours (allongés par <long pause>).
    Une pause dans une réplique peut être plus longue : toujours vérifier les durées obtenues."""
    db = niveaux(x)
    haut = db.max()
    parle = np.nonzero(db > haut - 48)[0]
    t_debut, t_fin = parle[0] * FEN, (parle[-1] + 1) * FEN
    candidats = [s for s in silences(db, haut - 48, 0.1) if s[0] > t_debut and s[1] < t_fin]
    if len(candidats) < n - 1:
        raise SystemExit(f"{len(candidats)} silences pour {n - 1} coupes : découpage impossible, le fichier complet reste utilisable.")
    coupes = sorted(sorted(candidats, key=lambda s: s[1] - s[0])[-(n - 1):]) if n > 1 else []
    debuts = [t_debut] + [b for _, b in coupes]
    fins = [a for a, _ in coupes] + [t_fin]
    return [(max(0.0, d - 0.02), f) for d, f in zip(debuts, fins)]


def cmd_decouper(a):
    _, tours = lire_dialogue(a.fichier)
    source = Path(a.audio)
    sorties = [source.parent / f"{a.debut + k:02d}_{qui.lower().replace(' ', '_')}.mp3" for k, (qui, _, _) in enumerate(tours)]
    for sortie in sorties:
        if sortie.exists() or sortie.with_suffix(".wav").exists():
            raise SystemExit(f"{sortie} existe déjà : on n'écrase rien.")
    x = lire_audio(source)
    morceaux = couper_aux_silences(x, len(tours))
    for sortie, (d, f), (_, _, texte) in zip(sorties, morceaux, tours):
        wav = sortie.with_suffix(".wav")
        ecrire_audio_brut(wav, fondu(x[int(d * SR): int(f * SR)].copy()))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-codec:a", "libmp3lame", "-b:a", "128k", str(sortie)], check=True)
        wav.unlink()
        print(f"{sortie.name} : {d:.2f} → {f:.2f} s ({f - d:.2f} s, {len(texte.split())} mots)  {texte}")


def main():
    p = argparse.ArgumentParser(description="Voix avec Gemini : une voix, un dialogue à deux voix, ou la découpe d'un dialogue")
    s = p.add_subparsers(dest="cmd", required=True)
    v = s.add_parser("voix")
    v.add_argument("--voix", required=True)
    v.add_argument("--style", default="")
    g = v.add_mutually_exclusive_group(required=True)
    g.add_argument("--texte")
    g.add_argument("--fichier")
    v.add_argument("--sortie", required=True)
    d = s.add_parser("dialogue")
    d.add_argument("fichier")
    d.add_argument("--sortie", required=True)
    for x in (v, d):
        x.add_argument("--modele", default=MODELE)
        x.add_argument("--simuler", action="store_true")
    c = s.add_parser("decouper")
    c.add_argument("fichier")
    c.add_argument("audio")
    c.add_argument("--debut", type=int, default=0, help="numéro de la première réplique")
    a = p.parse_args()
    {"voix": cmd_voix, "dialogue": cmd_dialogue, "decouper": cmd_decouper}[a.cmd](a)


if __name__ == "__main__":
    main()
