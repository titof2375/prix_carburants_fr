# Prix Carburants France - Intégration Home Assistant

Intégration Home Assistant pour récupérer les prix des carburants en France depuis l'API officielle du gouvernement.

## Fonctionnalités

- ✅ Récupération en temps réel des prix (mise à jour toutes les 10 minutes)
- ✅ Suivi GPS dynamique via n'importe quelle entité `device_tracker` ou `zone` (ex. `zone.home` pour une position fixe, ou un `device_tracker.xxx` pour suivre un téléphone en mouvement)
- ✅ Rayon de recherche configurable
- ✅ Nombre de stations à afficher configurable
- ✅ Prix et date de mise à jour par carburant, pour chaque station (`prix_gazole`, `date_gazole`, `prix_sp95`, `date_sp95`, etc. — détection automatique de tous les carburants présents dans les données)

## Installation

### Via HACS (recommandé)

Ce dépôt n'est pas dans le magasin par défaut de HACS, il faut donc l'ajouter comme **dépôt personnalisé** :

1. Ouvrez **HACS** dans la barre latérale de Home Assistant
2. Cliquez sur les **⋮** (trois points) en haut à droite → **Dépôts personnalisés**
3. Collez l'URL du dépôt : `https://github.com/titof2375/prix_carburants_fr`
4. Choisissez le type **Intégration**, puis cliquez sur **Ajouter**
5. Le dépôt "Prix des Carburants France" apparaît maintenant dans la liste HACS — cliquez dessus puis sur **Télécharger** (Download)
6. **Redémarrez Home Assistant**
7. Allez dans **Paramètres → Appareils et services → Ajouter une intégration**, recherchez **"Prix Carburants France"** et suivez le formulaire de configuration

Pour les mises à jour futures : HACS détecte automatiquement les nouvelles releases de ce dépôt (puisqu'il est déjà ajouté en dépôt personnalisé) — il suffit d'aller dans HACS, ouvrir l'intégration, et cliquer sur **Mettre à jour** quand une nouvelle version est proposée, puis redémarrer Home Assistant.

### Installation manuelle (alternative)

1. **Copiez le dossier** `prix_carburants_fr` dans votre dossier Home Assistant :

   ```
   homeassistant/custom_components/prix_carburants_fr/
   ```

2. **Redémarrez Home Assistant**

3. **Allez dans** Paramètres → Appareils et services → Ajouter une intégration

4. **Recherchez** "Prix Carburants France" et suivez le formulaire de configuration

## Configuration

Chaque instance de l'intégration suit **une seule** position GPS. Pour suivre plusieurs positions (ex. votre domicile et le téléphone d'une personne), ajoutez l'intégration plusieurs fois, une fois par position.

### Champs du formulaire

| Champ            | Exemple                          | Description                                                                 |
| ----------------- | --------------------------------- | ----------------------------------------------------------------------------- |
| `tracker_entity`  | `zone.home` ou `device_tracker.telephone_de_corinne` | Entité GPS à suivre — une zone fixe ou un tracker mobile |
| `name`            | `Prix Carburants Maison`          | Nom donné à cette instance de l'intégration                                  |
| `rayon_km`        | `20`                              | Rayon de recherche en kilomètres autour de la position                        |
| `nb_stations`     | `5`                               | Nombre de stations les moins chères à récupérer                              |

## Utilisation

### Capteurs créés

Un capteur `sensor.station_N` est créé pour chaque station trouvée (de 1 à `nb_stations`), par instance configurée.

### Attributs disponibles

Pour chaque capteur station, vous avez accès à :

- `name` : Nom de la station
- `address` : Adresse
- `postal_code` : Code postal
- `city` : Ville
- `latitude` / `longitude` : Coordonnées GPS
- `index` : Position dans le classement (1 = moins chère)
- `prix_<carburant>` : Prix du carburant (ex. `prix_gazole`, `prix_sp95`, `prix_sp98`, `prix_e10`, `prix_e85`, `prix_gplc`) — uniquement les carburants disponibles à cette station
- `date_<carburant>` : Date/heure de dernière mise à jour de ce prix par le gouvernement (ex. `date_gazole`)

L'état du capteur est le code postal + la ville de la station.

## API Source

Les données proviennent de l'API officielle du gouvernement français (Opendatasoft, v2.1) :

- **URL** : `https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/records`
- **Mise à jour source** : Toutes les 10 minutes
- **Licence** : Open License 2.0

## Développement futur

- [ ] Support du filtrage par type de carburant dans la requête
- [ ] Notifications quand le prix baisse
- [ ] Historique des prix
- [ ] Comparateur de stations

## Support

Pour signaler un bug ou une suggestion : [GitHub Issues](https://github.com/titof2375/prix_carburants_fr/issues)
