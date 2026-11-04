# Rôles des sons, et quand les utiliser

Chaque rôle correspond à un fichier `<rôle>.wav` de la bibliothèque. Les variantes `<rôle>1.wav`, `<rôle>2.wav`… sont alternées automatiquement. Le gain est un multiplicateur de 0 à 1, appliqué après avoir ramené la crête du son à −1 dBFS.

| Rôle | Quand | Gain conseillé | Décalage |
| --- | --- | --- | --- |
| `whoosh_fast` | un élément entre vite (titre qui glisse, changement d'écran rapide) | 0,4 – 0,6 | 0,1 – 0,15 s **avant** l'arrivée |
| `whoosh_soft` | transition douce, carte qui monte, fondu | 0,3 – 0,5 | 0,1 – 0,2 s avant |
| `pop` | une carte, une bulle, une étiquette ou un chiffre apparaît | 0,35 – 0,55 | pile à l'apparition |
| `click` | bouton, curseur, case cochée, petit détail d'interface | 0,3 – 0,5 | pile |
| `key` | frappe clavier ou texte qui s'écrit (variantes alternées) | 0,15 – 0,25 | un son toutes les 50 à 90 ms, irrégulier |
| `ding` | bonne réponse, validation ✓, fin, appel à l'action | 0,4 – 0,6 | pile |
| `impact` | gros titre qui tombe, chiffre-choc, coupure nette, slam | 0,6 – 0,9 | pile, jamais sous un mot clé de la voix |
| `impact_light` | accent plus léger (ligne de titre, carte importante) | 0,4 – 0,6 | pile |
| `glitch` | erreur, coupure « numérique », effet de bug | 0,3 – 0,5 | pile ; 1 seul par moment |
| `riser` | montée de tension avant une révélation ou une coupure | 0,5 – 0,7 | finit **sur** la révélation (`"coupe"` pour l'ajuster) |

Champs utiles d'un événement :

- `"coupe": 0.8` : coupe le son à 0,8 s avec un fondu, pour un riser trop long par exemple.
- `"fichier": "chemin.wav"` : un son hors bibliothèque, relatif au fichier d'événements.
- `"note"` : commentaire libre, ignoré par le script.

## Recettes de structure (vidéo de 12 à 20 s)
- **Accroche (0 à 1 s)** : `whoosh_fast` puis `impact_light` sur le titre. L'accroche doit « sonner » dès la première seconde.
- **Chaque nouvelle idée ou écran** : `whoosh_soft` à la transition, puis `pop` quand le texte arrive.
- **Chiffre-clé** : `impact` (ou `impact_light`) quand le chiffre apparaît, pas pendant que la voix le prononce.
- **Liste animée** (5 éléments qui arrivent) : un `pop` par élément si l'écart est ≥ 0,3 s, sinon un seul `pop` pour le groupe.
- **Quiz / vote** : `click` sur chaque option, `riser` pendant le compte à rebours, `ding` sur la bonne réponse.
- **Fin** : `ding` sur l'appel à l'action, ou un `impact` sur le logo, puis plus rien.

## Limites de la bibliothèque fournie (à signaler à l'écoute)
- `key` : coups de machine à écrire raccourcis à 0,14 s, qui peuvent sonner coupés. À remplacer par une vraie touche de clavier mécanique si possible.
- `impact_light` : choc sur du bois (bruitage réaliste), pas un « hit » de motion design.
- `glitch` : buzz d'erreur générique, pas un vrai glitch numérique.
- `pop` : sans marge à l'origine. Le script le normalise, mais garde son gain ≤ 0,55.
- Pas de nappe ni de musique : ce skill ne gère que les bruitages ponctuels.
