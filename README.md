# whatsapp-analyser
Python module for extracting some stats from exported Whatsapp discussions



## Comment utiliser le package ? 

Les instructions sont valables sur Mac et Linux, ceux sur Windows, à vos risque et péril...


1. Copier les fichiers avec git (sinon copier manuellement le projet) : `git clone https://github.com/karlmtr/wa-analyser.git`
2. Aller dans le dossier `cd wa-analyser`
3. Exécuter le script pour setup : `source setup.sh`
4. Mettre les disscusions sous format texte dans le dossier `data/`
5. Mettre le script `./run.sh` en exécutable : `chmod a+x run.sh`
6. Créer les graphiques en lançant le script: `./run.sh`



## TODOs

- [ ] Améliorer le graphique de messages par jour : `| lundi | mardi | mercredi | jeudi | ...`