# Automatisation de la production de la carte d'occupation des sols de Christophe Rousson

L'objectif est de pouvoir reproduire les classes d'occupation du sol de la carte de Christophe Rousson avec des données récentes et sur la France entière pour pouvoir les utiliser dans Fluvial Corridor Toolbox et ainsi reproduire les classes de continuité latérale.

La cartes n'a pas pu être reproduite à l'identique faute de d'information méthodologique mais permet de retrouver les zonages décris.

## Résumé de la reproduction de la carte d'occupation du sol

La production de la carte repose sur les donnée de la BD TOPO® de l'IGN ainsi que le Registre Parcellaire Graphique (RPG) pour les espaces agricoles pour une même année de production. Ces deux jeux de données supposent d'être stockés dans une base de données Postgresql/PostGIS pour l'execution des commandes SQL permettant l'extraction et les transformations des données spécifiques à chaque classe d'occupation du sol. La chaine de traitement d'execution des scripts SQL, de compilation des données et de rasterisation est effectuée par le fichier landuse.py. Un dernier jeux de données dans la base de données est nécessaire appelé 'zone_etude' correspondant à l'emprise spatiale sur laquelle la carte doit être produite. Elle est également utilisée pour définir les trous en 'naturel' une fois la compilation des classes effectuée.

La nouvelle nomenclature ci-dessous suite l'ordre de superposition de chaque classe lors de la compilation.

| Classe                             | Code       | Valeur | Description                                                                                                                                                  | Description technique                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|------------------------------------|------------|--------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Surface en eau                     | EAU        | 0      | Surface en eau permanente                                                                                                                                    | Les 'surface_hydrographique' de la BD TOPO avec l'attribut 'persistance' = 'Permanent' et 'nature' ≠ 'Glacier' et 'névé'                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Banc de galets, surfaces minérales | BANC       | 1      | Bancs sédimentaires correspondant aux zones en eau intermittentes                                                                                            | Les 'surface_hydrographique' de la BD TOPO avec l'attribut 'persistance' = 'Intermittent'                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Infrastructure de transport        | INFRA      | 8      | Infrastructure routières et férrovières définies par des zones tampons selon leur nature la largeur de la chaussée.                                          | Les 'troncon_de_route' de la BD TOPO avec une 'position_par_rapport_au_sol' = 0 ou 1, de 'nature' = 'Bretelle' ou 'Rond-point' ou 'Route à 1 chaussée' ou 'Route à 2 chaussées' ou Type autoroutier'  avec une zone tampon de la moitié de la 'largeur_de_chausse' sauf si la 'largeur_de_chausse' < 4 où la zone tampon est égal à 2. Les 'troncon_de_voie_ferree' de la BD TOPO avec une  'position_par_rapport_au_sol' = 0 ou 1 avec une zone tampon fonction de leur nature, soit de 15m pour une 'LGV', 8m pour une 'Voie ferrée principale' et 5m pour les autres. Les trous internes aux polygones créés < 500m2 sont remplis.                                                                                  |
| Naturel                            | NATUREL    | 2      | Zone de végétation ouverte                                                                                                                                   | Les 'zone_de_vegetation' de la BD TOPO avec l'attribut 'nature' = 'Haie' ou 'Lande ligneuse' ou 'Forêt ouverte' ou 'Zone arborée'. Les trous internes < 500m2 sont remplis. Une fois la compilation des classes effectuée, les espaces encore non qualifié dans la 'zone_etude' sont insérés dans cette classe.                                                                                                                                                                                                                                                                                                                                                                                                        |
| Bâti                               | BATI       | 7      | Zone continue de l'espace bâti dense ou artificialisée.                                                                                                      | Les polygones de la BD TOPO des couches 'batiment', 'construction_surfacique', 'cimetiere', 'reservoir', 'piste_d_aerodrome', 'equipement_de_transport' avec l'attribut 'nature' = 'Parking' ou 'Péage', 'zone_d_activite_ou_d_interet' avec l'attribut 'nature' = 'Usine' ainsi que 'construction_lineaire' avec une zone tampon de 2m. Une fermeture morphologique de 20m est appliqué pour créer une zone bâtie continu, soit une dilatation de 20 et une erosion de 20. Une zone tampon de 5m est ajouté à cette zone créée pour combler les petites surfaces. Les trous internes à cette surface < 2000m2 sont considéré comme étant intégré au bâti (remplissage) et les zones bâties <= 2500m2 sont supprimées. |
| Culture                            | CULTURES   | 5      | Zone de culture rassemblant les grandes cultures, l'arboricultre et les vignes.                                                                              | Les surfaces des parcelles graphiques du RPG rassemblées selon leur 'code_group'. Les grandes cultures correspondent aux groupes '1', '2', '3', '4', '5', '6', '7', '8', '9', '11', '14', '15', '16', '24', '25', '26', '28'. L'arboriculture correspond aux groupes '20', '22', '23'. La vigne correspond au groupe '21'. Ces trois sous-catégories sont rassemblées en une unique. Les trous internes  < 500m2 sont remplis.                                                                                                                                                                                                                                                                                         |
| Prairie permanente                 | PRAIRIE    | 4      | Zone de prairie permanente.                                                                                                                                  | Les surfaces des parcelles graphiques du RPG pour les 'code_group' '17' et '18'. Les trous internes < 500m2 sont remplis.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Forêt                              | FORET      | 3      | Zone de végétation fermée                                                                                                                                    | Les 'zone_de_vegetation' de la BD TOPO avec l'attribut 'nature' = 'Bois' ou 'Peupleraie' ou 'Forêt fermée mixte' ou 'Forêt fermée de feuillus' ou 'Forêt fermée de conifères'. Une fermeture morphologique de 20m (dilatation et érosion de 20m) est appliquée pour créer un zonage continu. Les trous < 500m2 sont remplis et les polygones < 2500m2 sont retirés.                                                                                                                                                                                                                                                                                                                                                    |
| Périurbain                         | PERIURBAIN | 6      | Zone identifiée comme n’étant ni urbanisé, ni agricole, ni forestier ni naturel et au contact d’une tâche urbaine. Correspond à la zone d'habitation diffus. | Les 'zone_d_habitation' de la BD TOPO avec une érosion de 20m pour ressérer cette zone un peu trop large. Les trous internes < 500m2 sont remplis et les polygones < 2500m2 sont retirés.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |

## Installation and workflow

### Create a python 3 virtual environment

Create a Python 3 virtual environment and install dependencies.

Windows

- Install python (made with Python 3.11.2) with environment PATH
- Install Git for windows
- Open a command prompt

```
# go to the working folder you want to download the mapdo application
cd Path/to/my/folder
# copy mapdo repository with git
git clone https://github.com/EVS-GIS/landuse-fct.git
# create a new virtual environnement in python 3
python3.11 -m venv env --prompt landuse-fct
# activate your new environment
.\env\Scripts\activate
# update pip
python -m pip install -U pip
# install dependencies
pip install -r requirements.txt
```

### Import the datasets

Two datasets need to be download :
- [BD TOPO® SQL version for metropolitan France](https://geoservices.ign.fr/bdtopo#telechargementsqlfra)
- [RPG Geopackage version for metropolitan France](https://geoservices.ign.fr/rpg)

Install Postgresql and create a database with PostGIS extension.

Import data from the datasets to the Postgresql database (example with data 2021 datasets). If zone_etude is a shapefile, it could be imported with QGIS or PostGIS Shapefile Import/Export Manager.

SQL table to import from IGN BD TOPO :
* BATI
  * batiment.sql
  * cimetiere.sql
  * construction_lineaire.sql
  * construction_surfacique.sql
  * reservoir.sql
* HYDROGRAPHIE
  * surface_hydrographique.sql
* TRANSPORT
  * troncon_de_route.sql
  * troncon_de_voie_ferree.sql
  * piste_d_aerodrome.sql
  * equipement_de_transport.sql
* SERVICES_ET_ACTIVITES
  * zone_d_activite_ou_d_interet.sql
* OCCUPATION_DU_SOL
  * zone_de_vegetation.sql
* LIEUX_NOMMES
  * zone_d_habitation.sql

Geopackage data to import from RPG :
* PARCELLES_GRAPHIQUES.gpkg

Import your zone_etude layer.

```
# Example in psql command with locahost database with BD TOPO SQL file

psql -U user -d my_database -f path/to/my/data/directory/BDTOPO_3-3_TOUSTHEMES_SQL_WGS84G_FRA_2022-12-15/BDTOPO/1_DONNEES_LIVRAISON_2022-12-00160/BDT_3-3_SQL_WGS84G_FRA-ED2022-12-15/TRANSPORT/troncon_de_voie_ferree.sql -h localhost

# Example import RPG geopackage file to PostgreSQL/PostGIS database with gdal (could be done also with QGIS)
ogr2ogr -f PostgreSQL PG:"dbname='my_database'" path/to/my/data/directory/RPG_2-0__GPKG_LAMB93_FXX_2021-01-01/RPG/1_DONNEES_LIVRAISON_2021/RPG_2-0_GPKG_LAMB93_FXX_2021-01-01/PARCELLES_GRAPHIQUES.gpkg -nln "rpg_parcelles_graphiques"

# Example import zone_etude.gpkg
ogr2ogr -f PostgreSQL PG:"dbname='my_database'" path/to/my/data/directory/landuse-fct/example_inputs/zone_etude.gpkg -nln "zone_etude"

```

### Workflow

To create the landuse map, a database.ini file need to be configurate with the Postgresql database parameters created. Rename config/example_config.ini file to config.ini then modify the parameters with the right configuration.

The database with datasets imported need to be prepare to set SRID, geometry columns, primary keys and spatial index before generate landuse map. In command prompt in landuse directory and with activated virtual environment.

**WARNING, the operation could be time consuming if you have loaded the whole France**

```
# Run database_preparation.py
python database_preparation.py

# run landuse.py to create landuse raster and vector files
python landuse.py
```

The *output* directory gather the final files.

## Démarche de la reproduction

Un script de Christophe Rousson a été retrouvé sur [github](https://github.com/sdunesme/fct-cli/blob/master/landcover/rasterize_bdt.py). Il est malheureusement incomplet, c'était un script de travail en cours supprimé par la suite.

On retrouve plusieurs méthode et nomenclature dans les documents de thèse de Christophe Rousson. La version utilisée qui semble la plus à jour est dans le [tableau des données et des métriques EBF](https://gitlab.huma-num.fr/evs/mapdo/-/blob/main/landuse/doc/Tableaux%20des%20donn%C3%A9es%20et%20des%20m%C3%A9triques%20EBF.pdf), voir Tableau 9 – Nomenclature de la carte d’occupation du sol (v2 raster). Il y a aussi des informations méthodologique dans le document de [l'occupation du sol à grande échelle](https://gitlab.huma-num.fr/evs/mapdo/-/blob/main/landuse/doc/Occupation%20du%20sol%20%C3%A0%20grande%20%C3%A9chelle.pdf). Les méthodes expliquées ne sont cependant pas tout à fait similaire malgré une nomenclature identique.

La méthode de Christophe Rousson est basée sur la nomenclature du RPG de 2014, or elle a été modifiée en 2015 et les données récentes suivent la nouvelle nomenclature. Les modifications apportées sont décrites dans le [descriptif de livraison de l'IGN](https://gitlab.huma-num.fr/evs/mapdo/-/blob/main/landuse/doc/DC_DL_RPG_2-0.pdf) (2021).
Quelques modifications ont été apporté à la méthode pour suivre [la nouvelle nomenclature](https://gitlab.huma-num.fr/evs/mapdo/-/blob/main/landuse/doc/REF_CULTURES_GROUPES_CULTURES_2020.csv) : 
- pour l'arboriculture le code_group du 27 rejoint le 20. On n'a plus que 20, 22 et 23 dans cette catégorie.

La nomenclature de la BD TOPO a été modifié avec la version 3.0. BATI_REMARQUABLE n'existe plus par exemple. Une correspondance peut-être établi avec les descriptifs de livraison [2.08](https://gitlab.huma-num.fr/evs/mapdo/-/blob/main/landuse/doc/DC_BDTOPO_2_08.pdf) et [3.3](https://gitlab.huma-num.fr/evs/mapdo/-/blob/main/landuse/doc/DC_BDTOPO_3-3.pdf) : 
- Aérogare : regroupé dans batiment indifférenciée
- Arc de triomphe : dans batiment nature
- Arène ou théâtre antique : dans batiment nature
- Bâtiment religieux divers
- Bâtiment sportif : les gynmase sont dans batiment indifférenciée et un nouveau thème à les terrain de sport
- Chapelle - batiment nature
- Château - batiment nature
- Eglise - batiment nature
- Fort, blockhaus, casemate - batiment nature
- Gare : regroupé dans batiment indifférenciée
- Mairie : regroupé dans batiment indifférenciée
- Monument - batiment nature
- Péage - regroupé dans batiment nature Industriel, agricole ou commercial
- Préfecture : regroupé dans batiment indifférenciée
- Sous-préfecture : regroupé dans batiment indifférenciée
- Tour, donjon, moulin - batiment nature (deux catégories)
- Tribune - batiment nature

Les suivis d'évolution des versions de la BD TOPO est disponible sur le site de l'IGN mais on ne retrouve pas de descriptif détaillé pour passer de l'ancienne à la nouvelle nomenclature.

Les classes BATI_INDIFFERENCIE, BATI_REMARQUABLE et BATI_INDUSTRIEL de l'ancienne nomenclature sont regroupés dans la classe batiment dans la version 3.3. On retrouve les classes cimetière, réservoir, terrain de sport, construction linéaire et construction surfacique. Les constructions légères sont maintenant une variable de la classe batiment. Les polygones des pistes d'aérodrome sont maintenant dans le thème transport, classe piste d'aérodrome.

Pour résumer, pour retrouver les éléments de la classe BATI de Christophe Rousson avec la nomenclature 3.3 de la BD TOPO il faut reprendre tous les éléments des classes batiment, construction_lineaire, construction_surfacique, cimetiere, reservoir, terrain_de_sport du thème BATI et ajouter tous les éléments de la classe piste_d_aerodrome du thème TRANSPORT.

On ne trouve cependant pas de précisions sur le traitement de la couche construction_lineaire dans la classe BATI de la nomenclature de Christophe Rousson. Il faut transfomer ces lignes en polygone pour pouvoir les associer aux autres éléments de la classe. Un buffer de 2m a été appliqué, le même que les opérations morphologiques même si ces opérations sont effectuées après compilation des polygones.

La classe PERIURBAIN est peu clair dans la documentation. La zone d'habitation de la BD TOPO a été utilisé avec une érosion de 20m car cette couche est un peu plus large que le bâti.