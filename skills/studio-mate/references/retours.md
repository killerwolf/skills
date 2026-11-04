# Traduire les retours d'Hamdi en Notion

Les propriétés de la base 🎞️ Vidéos sont à recopier **au caractère près**, emoji compris : les agents du studio les lisent telles quelles. Recopie les noms d'options depuis la base elle-même, avec `notion-fetch` de la base. Plusieurs emoji (✍️, 🎙️, 🗑️) portent un caractère invisible que la frappe peut perdre.

Avant d'écrire, vérifie « Agent / En cours » (`SKILL.md`, règle 4). Après chaque ligne de ce tableau : une ligne au Journal, puis une phrase de confirmation à Hamdi.

| Hamdi dit… | Tu fais |
|---|---|
| « OK », « c'est bon » pour une vidéo relue | « Retour du validateur » : ajoute « Hamdi : relecture OK (AAAA-MM-JJ) ». Statut → 📅 Programmée. S'il donne une date, mets-la dans « Date de publication » ; sinon le Validateur attribuera un créneau. Vide « 👤 À faire (Hamdi) ». |
| Des remarques sur une vidéo | « Retour du validateur » : « Hamdi : » suivi de ses mots **exacts**, puis une reformulation en consignes précises (une par ligne). Statut → 🎬 Rendu. Vide « 👤 À faire (Hamdi) ». La Production les appliquera. |
| « Je garde telle et telle idée » | Ces idées → ✅ Validée. S'il donne une priorité, mets-la dans « Priorité ». |
| « Non » à une idée | Statut → 🗑️ Abandonnée. Ne supprime jamais la page. |
| Une nouvelle idée | Crée une page dans 🎞️ Vidéos : Titre, Format (📱 Short ou 🎬 Long, demande s'il ne dit rien), Série et Thème s'il les donne, Accroche (sa phrase), et deux lignes d'angle dans la page. Statut 💡 Idée, ou ✅ Validée s'il dit qu'il la veut. |
| La réponse à un blocage (⛔) | « Retour du validateur » : « Hamdi : » suivi de sa réponse. Vide « Blocage » et « 👤 À faire (Hamdi) ». Renvois → 0. Statut → l'étape d'avant le blocage, celle que le Journal ou la page indiquent ; en cas de doute, demande. |
| Une date pour une vidéo | « Date de publication » → la date et l'heure de Paris qu'il donne. |
| Un lien YouTube d'**une de ses vidéos** | Colle-le dans « Lien YouTube ». Le Statut reste 📅 Programmée : le Validateur passera en 🚀 Publiée après avoir vérifié qu'elle est en ligne. |
| Un lien vers **une autre chaîne** (« surveille ça ») | Ajoute-le dans la section « 📡 Chaînes à surveiller » du hub, avec son commentaire. La Veille l'inscrira. |
| « Mets telle vidéo en priorité » | « Priorité » → la valeur la plus haute de la base. |
| « Abandonne telle vidéo » | Statut → 🗑️ Abandonnée, avec la raison dans « Retour du validateur » (« Hamdi : … »). Demande confirmation si la vidéo est déjà en 🎙️ Voix ou au-delà : des crédits ont déjà été dépensés. |

## Ce que tu ne fais jamais
- Passer une vidéo en 🚀 Publiée : c'est le Validateur, après vérification en ligne.
- Effacer un retour existant : tu ajoutes une ligne, tu ne remplaces pas.
- Remplir « Agent / En cours » pour toi : tes modifications sont immédiates, et tu n'as rien à réserver.
