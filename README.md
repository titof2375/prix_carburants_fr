# Prix Carburants France - Intégration Home Assistant

Intégration Home Assistant pour récupérer les prix des carburants en France depuis l'API officielle du gouvernement.

## Fonctionnalités

- ✅ Récupération en temps réel des prix (mise à jour toutes les 10 minutes)
- ✅ Support de deux localisations : Maison et Téléphone (via GPS)
- ✅ Rayon de recherche configurable
- ✅ Affichage du nombre de stations configurable
- ✅ Support de tous les types de carburants (Gazole, SP95, SP98, E85, GPLc, SP95-E10)
- ✅ Dates d'actualisation des prix incluses

## Installation

1. **Copiez le dossier** `prix_carburants_fr` dans votre dossier Home Assistant :
   ```
   homeassistant/custom_components/prix_carburants_fr/
   ```

2. **Redémarrez Home Assistant**

3. **Allez dans** Paramètres → Appareils et services → Créer une automatisation

4. **Recherchez** "Prix Carburants France" et cliquez sur Créer une configuration

5. **Entrez vos paramètres** :
   - Latitude/Longitude de votre maison
   - Latitude/Longitude de votre téléphone
   - Rayon de recherche (en km)
   - Nombre de stations à afficher

## Configuration

### Exemple de configuration

| Paramètre | Exemple | Description |
|-----------|---------|-------------|
| Latitude Maison | 46.57 | Latitude de votre domicile |
| Longitude Maison | 2.42 | Longitude de votre domicile |
| Latitude Téléphone | 46.58 | Latitude actuelle (téléphone) |
| Longitude Téléphone | 2.43 | Longitude actuelle (téléphone) |
| Rayon de recherche | 20 | Rayon en km autour des GPS |
| Nombre de stations | 5 | Nombre de stations à afficher |

## Utilisation

Après l'installation, vous aurez accès à :

### Capteurs créés

- **Stations près du téléphone** : Affiche les N meilleures stations avec les prix
- **Stations près de la maison** : Affiche les N meilleures stations avec les prix

### Attributs disponibles

Pour chaque station, vous avez accès à :
- `nom_station` : Nom de la station
- `marque` : Marque (Carrefour, Leclerc, etc.)
- `adresse` : Adresse complète
- `latitude` / `longitude` : Coordonnées GPS
- `distance_km` : Distance depuis votre position
- `derniere_maj` : Dernière mise à jour
- `prix_gazole`, `prix_sp95`, etc. : Prix de chaque carburant
- `date_gazole`, `date_sp95`, etc. : Date de mise à jour de chaque carburant

## API Source

Les données proviennent de l'API officielle du gouvernement français :
- **URL** : https://data.economie.gouv.fr/explore/dataset/prix-des-carburants-en-france-flux-instantane-v2/api/
- **Mise à jour** : Toutes les 10 minutes
- **Licence** : Open License 2.0

## Développement futur

- [ ] Support du filtrage par type de carburant
- [ ] Notifications quand le prix baisse
- [ ] Historique des prix
- [ ] Comparateur de stations

## Support

Pour signaler un bug ou une suggestion : [GitHub Issues](https://github.com/utilisateur/prix_carburants_fr/issues)
