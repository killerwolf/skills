# La page « 🗂️ Mes studios » : l'annuaire

Studio Mate ne connaît qu'une page : celle-ci. Elle dit, pour chaque studio, où se trouvent son hub, ses vues, son Journal et sa Salle de relecture. **Ajouter un studio, c'est ajouter une section.** Pas de code, pas de fichier.

## Forme de la page
Une page Notion simple, titrée exactement **🗂️ Mes studios**, à la racine de l'espace d'Hamdi ou à l'endroit qu'il choisit. Une section par studio :

```markdown
## <Nom exact de la chaîne>
- Hub : <lien de la page hub>
- Salle de relecture : <lien claude.ai de la Salle>
- 👤 Mes actions (Hamdi) : view://…
- 💡 Idées à valider : view://…
- 📅 Calendrier de publication : view://…
- 🗂️ Pipeline : view://…
- 🤖 Journal (récent) : view://…
- Base Vidéos : <lien de la base 🎞️ Vidéos>
- Base Journal : <lien de la base 🧾 Journal>
- Horaires du Mac : <ex. 7 h–13 h et 20 h–22 h, heure de Paris>
- Remarque : <facultatif ; ex. « en pause jusqu'au 15 »>
```

Les adresses `view://…` sont dans le `STUDIO.md` de chaque studio, et visibles avec `notion-fetch` de la base Vidéos.

## La créer avec Hamdi (première fois)
1. Demande-lui les **liens des hubs** de ses studios, une ligne par studio.
2. Pour chaque hub : `notion-fetch` du hub, puis de la base 🎞️ Vidéos et de la base 🧾 Journal, pour relever les vues par leur **nom exact** et le lien de la Salle (première ligne du bloc 📌 du hub).
3. Montre-lui le contenu de la page **avant** de la créer, puis crée-la (`notion-create-pages`) à l'endroit qu'il choisit.
4. Teste chaque vue en mode `view`. Une vue qui ne répond pas reste dans la page avec « ⚠️ à vérifier » à côté.

## La tenir à jour
- Nouveau studio : ajoute sa section, en reprenant les étapes 2 et 3 pour ce seul studio.
- Studio arrêté : n'efface rien. Ajoute « Remarque : arrêté le AAAA-MM-JJ » ; Studio Mate l'ignore dans « qu'est-ce que j'ai à faire ? ».
- Une vue renommée ou recréée dans un studio : mets son adresse à jour ici.
