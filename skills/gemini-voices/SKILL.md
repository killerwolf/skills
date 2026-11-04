---
name: gemini-voices
description: Génère des voix de vidéo avec Gemini (narration, personnages, dialogue à deux voix) puis découpe le dialogue en une réplique par fichier, pour n'importe quel projet ou studio vidéo. Déclencheurs : « voix Gemini », « génère cette voix avec Gemini », « essaie cette réplique avec Gemini », « génère ce dialogue avec Gemini », « découpe ce dialogue ».
---

# Voix de vidéo avec Gemini

**Les règles du projet courant passent avant ce skill.** Lis d'abord ses instructions (`CLAUDE.md`, guide de style) : voix autorisées, droit de générer, dossiers, noms de fichiers, niveaux sonores, versionnement. Si le projet n'autorise pas la génération ou si la voix n'y est pas prévue, demande à la personne avant de lancer.

## Prérequis
- **`uv`** : il installe tout seul ce dont le script a besoin. Sans `uv` : `pip install "google-genai>=2.34" numpy`, puis `python "${CLAUDE_SKILL_DIR}/scripts/gemini_voix.py" …`.
- **`ffmpeg`**.
- **La clé** : `GEMINI_API_KEY` dans l'environnement, sinon dans un `.env` du dossier courant ou d'un dossier parent. Vérifie que ce `.env` est bien ignoré par git. La clé n'est jamais affichée, écrite ailleurs ni demandée dans la conversation : la personne la colle elle-même.

## Règles
- **Une génération = un appel.** Annonce le nombre d'appels avant de lancer.
- **Jamais de relance** pour « réessayer » ni de boucle d'essais. Pour vérifier sans dépenser : `--simuler`.
- **Quota épuisé** (`RESOURCE_EXHAUSTED`) : arrête-toi et préviens. Le quota du jour revient à minuit heure du Pacifique. Les chiffres exacts sont dans Google AI Studio.
- **Le script n'écrase jamais un fichier existant** : change le nom de sortie.
- **Lance le script depuis le dossier du projet**, pour qu'il trouve son `.env`.

## Commandes
`${CLAUDE_SKILL_DIR}` est le dossier de ce skill.

Une voix :
```
"${CLAUDE_SKILL_DIR}/scripts/gemini_voix.py" voix --voix Algenib --style "vieil homme bourru" --texte "C'est qui, là dehors ?" --sortie audio/05_portier.mp3
```

Un dialogue à deux voix, en un seul appel :
```
"${CLAUDE_SKILL_DIR}/scripts/gemini_voix.py" dialogue dialogue.txt --sortie audio/dialogue.mp3
```

Le fichier de dialogue donne d'abord les voix, puis une réplique par ligne (personnage | style | texte) :
```
@Portier = Algenib
@Voyageur = Puck
Portier | vieil homme bourru | C'est qui, là dehors ?
Voyageur | jeune bourgeois outré | Pardon ?
```

Puis une réplique par fichier, sans appel (`--debut` = numéro de la première) :
```
"${CLAUDE_SKILL_DIR}/scripts/gemini_voix.py" decouper dialogue.txt audio/dialogue.mp3 --debut 5
```

Résultat : `<NN>_<personnage>.mp3`, en MP3 mono, 128 kb/s. Le `.wav` d'origine de Gemini reste à côté du fichier complet.

## Vérifier la découpe
La découpe coupe aux silences les plus longs. Même avec le `<long pause>` que la commande `dialogue` ajoute entre les répliques, **vérifie toujours la durée de chaque fichier** (environ 3 mots par seconde ; le script affiche les deux) : une pause dans une phrase peut être plus longue qu'une pause entre deux répliques.

Si c'est faux, découpe à la main, sans nouvel appel : repère les bornes avec le filtre `silencedetect` de `ffmpeg`, et distingue les voix à leur hauteur si besoin. Une réplique générée seule par `voix` n'a rien à découper.

## Choisir la voix, le style et le modèle
- **Voix** : `--voix`, ou les lignes `@Personnage = Voix` du dialogue. Exemples : Algenib (rocailleuse), Puck (enjouée), Charon (informative), Gacrux (mûre), Leda (jeune), Sulafat (chaude), Achird (amicale). Liste complète : https://ai.google.dev/gemini-api/docs/speech-generation
- **Style** : `--style`, ou la colonne du milieu du dialogue, en mots simples (« voix de jeune femme enjouée »).
- **Modèle** : `--modele` (par défaut `gemini-3.8-flash-tts`).
- **Plus de deux voix** : Gemini en accepte 2 au maximum par appel. Pour 3 voix, compte 2 appels : `dialogue` avec les deux voix qui parlent le plus, puis `voix` pour la troisième.

## Écrire pour Gemini
- Gemini lit le texte tel quel : **pas de balises entre crochets** comme `[annoyed]` (le script les refuse). Le ton va dans le style.
- Sons ponctuels entre chevrons : `<laugh>`, `<sigh>`, `<short pause>`.
- Écris les nombres en lettres et évite les guillemets.

## Après la génération
Le script affiche la durée et la sonie. **Écoute le résultat avant de conclure**, ou demande à la personne de l'écouter. Il ne versionne rien et ne touche pas au montage : suis les règles du projet pour la suite.
