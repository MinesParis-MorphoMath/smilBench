

  Benchmarks comparatifs entre SmilPython et scikit-image

  Repertoires :

    images/          images de test

    jose-desktop/    resultats machine perso a Fontainebleau
    nestor/          resultats machine perso at home
    taurus/          resultats machine de calcul taurus


  OBS : 
  1 - Les temps d'exécution comparés sont ceux des appels des fonctions
      en Python, à l'aide du module "timeit"
  2 - Pour l'instant, la qualité des résultats n'est pas examinée.
  3 - Noms des fichiers de résultats suivent la logique :
        imtype-imname-fonction.txt
        * imtype   : bin (binaire) ou gray (256 niveaux)
        * imname   : nom de l'image (sans extension)
        * fonction : function à comparer
