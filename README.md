# Pricing d'Options Américaines : Méthode de Longstaff-Schwartz 📈

## 📋 Description du Projet

**Dates de réalisation :** 20 Novembre 2025 – 29 Novembre 2025  

Il s'agit de mon premier projet en finance de marché. L'objectif principal est de valoriser des options américaines (Call/Put) via la méthode de Longstaff-Schwartz et de comparer la précision obtenue avec le modèle de Black-Scholes et une simulation de Monte Carlo classique pour les options européennes.

Contrairement aux options européennes, **les options américaines peuvent être exercées à tout moment** avant leur maturité. Cette caractéristique d'exercice anticipé génère un problème "d'arrêt optimal" (Optimal Stopping) qui rend les modèles de pricing classiques inopérants. L'enjeu de ce projet est d'utiliser la simulation de Monte Carlo couplée à une régression par moindres carrés pour estimer la frontière d'exercice optimal.

---

## 📚 Concepts Théoriques

### 1. Dynamique de Black-Scholes
On considère un actif sous-jacent dont le prix $S_t$ suit l'équation différentielle stochastique standard :
$$\frac{dS_{t}}{S_{t}}=(r-q)dt+\sigma dW_{t}$$
Où $r$ est le taux sans risque, $q$ le taux de dividende continu et $\sigma$ la volatilité.

### 2. Méthode de Longstaff-Schwartz (LS)
Le pricing d'une option américaine par simulation pose un défi majeur : déterminer à chaque instant $t$ s'il est préférable d'exercer l'option ou de la conserver. La décision repose sur la comparaison entre :
1. **La valeur intrinsèque d'exercice immédiat** (Payoff) : $h(S_t)$
2. **La valeur de continuation** : l'espérance actualisée de la valeur de l'option conditionnelle à l'information disponible au temps $t$.

L'algorithme de Longstaff et Schwartz (2001) utilise une **régression par moindres carrés** (ici via une base de polynômes de Laguerre) sur les trajectoires simulées pour estimer cette espérance conditionnelle de continuation.

---

## 🛠️ Outils et Technologies

Ce projet s'appuie sur un écosystème Python robuste pour la finance quantitative :
- **numpy** : Calcul matriciel, vectorisation et gestion des trajectoires stochastiques.
- **scipy.special (ndtr)** : Calcul de la fonction de répartition de la loi normale (pricer BS).
- **numpy.polynomial.laguerre** : Implémentation de la régression polynomiale robuste.
- **yfinance** : Récupération des données historiques de marché (AAPL, TTE.PA, etc.).
- **matplotlib / seaborn** : Visualisation des trajectoires et analyse de convergence MCMC.

---

## 📁 Architecture du Projet

Pour garantir un code propre et reproductible, le projet est structuré de manière modulaire :

```
Pricing_American_Options_LS/
│
├── docs/
│   └── longstaff_schwartz_theory.md   # Dérivations mathématiques de l'algorithme
│
├── src/
│   ├── generators.py        # Génération de nombres aléatoires (Box-Muller)
│   ├── models/
│   │   ├── black_scholes.py # Formules analytiques et Monte Carlo Européen
│   │   └── american_ls.py   # Coeur du pricer Longstaff-Schwartz
│   └── utils/
│       └── market_data.py   # Intégration yfinance et interpolation des taux OAT
│
├── notebooks/
│   ├── 01_theoretical_bench.ipynb  # Validation du modèle sur actifs théoriques
│   └── 02_market_analysis.ipynb    # Pricing sur données réelles (TTE.PA, LVMH, AAPL)
│
├── requirements.txt         # Dépendances du projet
└── README.md                # Ce fichier
```
---

## 📚 Références & Bibliographie

Ce projet s'appuie sur les travaux académiques et outils suivants :

1. **Longstaff, F. A., & Schwartz, E. S. (2001)**. *Valuing American Options by Simulation: A Simple Least-Squares Approach*. The Review of Financial Studies, 14(1), 113-147. (Pour l'algorithme d'arrêt optimal par régression).
2. **Black, F., & Scholes, M. (1973)**. *The Pricing of Options and Corporate Liabilities*. Journal of Political Economy, 81(3), 637-654. (Pour le benchmark européen).
3. **Box, G. E. P., & Muller, M. E. (1958)**. *A Note on the Generation of Random Normal Deviates*. Annals of Mathematical Statistics. (Pour la génération des trajectoires stochastiques).
4. **Données de marché** : Extraites via l'API [yfinance](https://pypi.org/project/yfinance/).
5. **Taux d'intérêt** : Courbe des taux OAT interpolée à partir des données de la Banque de France.