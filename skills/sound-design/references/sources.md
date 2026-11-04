# Ajouter ou remplacer des sons (CC0)

**Règle** : CC0 (domaine public) de préférence. Sinon, une licence vérifiée sur la page du son, et le crédit affiché là où le projet l'exige. Chaque fichier ajouté a une entrée dans `credits.json` : `file`, `role`, `source_pack`, `author`, `license`, `page_url`, `original_filename`. Ne prends jamais de son extrait d'une vidéo, d'un jeu ou d'un film existant.

Travaille dans une **copie de la bibliothèque propre au projet** (`--biblio DOSSIER` ou `SOUND_DESIGN_LIB`). La bibliothèque fournie dans `assets/sfx/` sert de base.

## Freesound (le plus riche)
- Il faut une clé gratuite, `FREESOUND_API_KEY` (https://freesound.org/apiv2/apply), et un réseau qui laisse passer `freesound.org` et `cdn.freesound.org`.
- Chercher (CC0 seulement, triés par note) :
  `python3 "${CLAUDE_SKILL_DIR}/scripts/sound_design.py" freesound chercher "mechanical keyboard key" --max-duree 0.5`
- Ajouter, avec l'aperçu HQ en mp3, la conversion en WAV 48 kHz et le crédit noté :
  `python3 "${CLAUDE_SKILL_DIR}/scripts/sound_design.py" freesound prendre <id> --role key4 --biblio DOSSIER`
- Erreurs fréquentes :
  - **401** : la clé est refusée.
  - **403 sans corps** : le réseau est bloqué. C'est souvent le cas depuis un conteneur cloud : Freesound refuse certaines IP de datacenter. Fais-le en local.

## OpenGameArt (joignable depuis le cloud, sans clé)
- Recherche des effets sonores : `https://opengameart.org/art-search-advanced?keys=<mots>&field_art_type_tid%5B%5D=13`.
- Vérifie le champ **License** de la page (CC0). Les liens de téléchargement sont sous `/sites/default/files/…`.
- Très bons packs CC0 : « Interface Sounds » (Kenney), « 18 Random Video Game Sound Effects » (bart), « 75 CC0 Breaking Falling Hit SFX » (rubberduck).
- Télécharge dans un **dossier temporaire vide, hors du projet**. N'exécute rien de ce qui est téléchargé. Puis convertis :
  `ffmpeg -i source.ogg -af silenceremove=start_periods=1:start_threshold=-50dB -ar 48000 -ac 2 -c:a pcm_s16le <rôle>.wav`
  (avec `atrim` et `afade` pour raccourcir), et ajoute l'entrée dans `credits.json` à la main.

## Choisir un son (sans pouvoir l'écouter)
- **Durée** : courte selon le rôle (voir `roles.md`). Coupe avec un fondu de 0,1 à 0,15 s si besoin.
- **Attaque nette** : après `silenceremove`, le son doit commencer tout de suite. Contrôle avec `silencedetect`.
- **Niveau** : `volumedetect`. Une crête à 0 dB n'est pas grave, le script normalise ; mais un niveau moyen très bas signale souvent un son presque vide.
- **Garde 2 ou 3 candidats**, propose-les à l'écoute, puis supprime ceux qui sont rejetés.
