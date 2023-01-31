# DiscoRSS

Le bot DiscoRSS permet d'exporter sa veille collective depuis discord vers une page internet.

## Exemple d'usage:

*********** est une association d'intérêt écologiste. Son serveur discord est le lieu de débats où des références pertinentes sur l'écologie sont couramment partagées au fil des discussions des utilisateurs. Les sources partagées qui constituent une veille collective sont référencées puis affichées sur la page dédiée DiscoRSS de l'association. La veille peut alors être partagée à des personnes qui ne souhaitent pas utiliser discord.

## Installation

Pour installer le bot sur votre serveur. Contactez moi (levez une issue par exemple).

L'installation se fait par l'adminsitrateur du serveur en invitant le robot grâce à un lien que je vous fournirai.

## Esprit:
- Léger: le site internet doit peser moins de 10 Ko.
- Anonyme: aucune information identifiante sur les utilisateurs discord n'est stockée en base.
- Détendu: pas d'interaction toxique sur le site.

## Trucs techniques

To run the project locally you need to:
- setup the database (once)
- launch the website
- launch the bot


Create the database from scratch and set alembic head to current state

    python scripts/create_database.py

Test server page:

    http://127.0.0.1:5000/1041036125894082621
