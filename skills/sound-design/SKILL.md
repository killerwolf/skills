---
name: sound-design
description: Ajoute du sound design à une vidéo courte (TikTok, Reels, Shorts, promo) — whooshs, pops, impacts, frappe clavier, ding — calé sur les apparitions de texte et les transitions, mixé sous la voix, avec une bibliothèque de sons CC0 fournie et extensible (OpenGameArt, Freesound). Déclencheurs : « sound design », « bruitages », « SFX », « ajoute des sons », « plus punchy », « ça manque de son quand le texte apparaît », « remplace ce son ». À utiliser aussi d'office quand on fabrique une vidéo avec texte animé et voix off.
---

# Sound design de vidéo courte

**Les règles du projet courant passent avant ce skill.** Lis d'abord ses instructions (`CLAUDE.md`, `AGENTS.md`, guide de style) : public visé (enfants = sons doux), règles de son, dossiers, versionnement. Si le projet interdit les bruitages ou en a déjà, demande avant de changer quoi que ce soit.

But : la voix porte l'émotion, les bruitages donnent du relief à l'image. Chaque élément qui apparaît, change ou frappe à l'écran a un son court. Mais ces sons restent **sous** la voix et ne fatiguent pas l'oreille.

## Prérequis
- `python3` (bibliothèque standard seulement) et `ffmpeg` / `ffprobe`.
- Optionnel : `FREESOUND_API_KEY`, pour ajouter des sons Freesound (voir `references/sources.md`).

`${CLAUDE_SKILL_DIR}` est le dossier de ce skill. Le script : `${CLAUDE_SKILL_DIR}/scripts/sound_design.py`.

## Méthode (une vidéo)
1. **Repérer les moments** à sonoriser, sur l'image et pas seulement dans le texte : timeline de la scène (instants où un titre, une carte, un chiffre apparaît ; transitions ; frappe), `narration.json` (où la voix parle). Si rien de tel n'existe, extrais quelques images (`ffmpeg -ss T -frames:v 1`) pour situer les apparitions.
2. **Brouillon** (facultatif, à partir de la narration) :
   ```
   python3 "${CLAUDE_SKILL_DIR}/scripts/sound_design.py" brouillon --narration narration.json --duree 15 --sortie sfx_events.json
   ```
   C'est une proposition grossière : **recale chaque `t` sur l'image**, retire, ajoute.
3. **Écrire `sfx_events.json`** : un événement = un instant, un rôle, un gain (0 à 1). Vocabulaire et dosage : `references/roles.md`. Garde le fichier à côté de la vidéo : c'est la partition sonore, versionnable et modifiable.
4. **Poser** les sons → une piste de bruitages :
   ```
   python3 "${CLAUDE_SKILL_DIR}/scripts/sound_design.py" poser sfx_events.json --sortie sfx.wav
   ```
5. **Mixer** sous le son existant. Si tu as la voix seule, passe-la avec `--voix` : les bruitages s'effacent quand elle parle.
   ```
   python3 "${CLAUDE_SKILL_DIR}/scripts/sound_design.py" mixer video.mp4 sfx.wav --sortie video_sfx.mp4 --gain-db -4 [--voix voix.wav]
   ```
   Si le projet a son propre pipeline de mix, utilise plutôt `sfx.wav` comme une piste de plus, au même niveau relatif.
6. **Vérifier** (tu ne peux pas écouter, alors mesure) :
   ```
   python3 "${CLAUDE_SKILL_DIR}/scripts/sound_design.py" verifier video_sfx.mp4
   ```
   - Crête ≤ −1 dBFS.
   - Niveau moyen proche de l'original (± 2 dB), sauf si le projet veut plus de punch.
   - Aucune tranche soudain beaucoup plus forte que ses voisines.
7. **Demander une écoute humaine** avant de publier, et dire précisément quels sons sont les plus risqués (voir « Limites » dans `references/roles.md`).

## Règles de mix
- Bruitages **6 à 10 dB sous la voix** quand elle parle. Par défaut, `--gain-db -4` sur la piste, avec des gains d'événement de 0,3 à 0,7.
- **Pas plus de 3 sons agressifs par seconde** (impacts, glitchs). Les frappes clavier sont exemptées : elles restent douces, gain ≤ 0,25.
- **Un son par apparition**, pas par lettre ni par élément d'une liste animée : un seul pop pour un groupe.
- **Pas d'impact sous un mot important** de la voix : décale de 0,1 à 0,2 s avant ou après.
- **Enfants** : pops, dings et whooshs doux ; pas d'impacts lourds ni de glitchs.
- **Fin de vidéo** : un ding ou un impact final, puis silence ou fondu. Jamais de son coupé net.

## Au quotidien
- **On fabrique un épisode** : fais la méthode sans attendre qu'on le demande, si le projet a du texte animé et une voix.
- **« Plus punchy » / « plus doux »** : change les gains et les rôles (impact ↔ impact_light, whoosh_fast ↔ whoosh_soft), pas le niveau global seul.
- **« Ce son est moche »** : remplace-le dans la bibliothèque (`references/sources.md`). Garde l'ancien sous un autre nom tant que la personne n'a pas validé.
- **« Pas de bruitages »** : n'en mets pas, et note-le dans les notes du projet si elles existent.

## Bibliothèque
`python3 "${CLAUDE_SKILL_DIR}/scripts/sound_design.py" biblio` liste les rôles, les variantes, les auteurs et les licences.

12 sons CC0 sont fournis dans `assets/sfx/`. Pour travailler sur une copie du projet : `--biblio DOSSIER` ou `SOUND_DESIGN_LIB`. C'est conseillé dès qu'on ajoute des sons, pour ne pas modifier le skill installé. Ajouter, remplacer, créditer : `references/sources.md`.

**Que des sons CC0 ou de licence vérifiée.** Note toujours l'auteur et la page dans `credits.json`, même pour du CC0. Ne jamais prendre un son d'une vidéo, d'un jeu ou d'un film existant.
