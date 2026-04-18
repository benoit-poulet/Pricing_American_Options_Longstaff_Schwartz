# Étude Théorique de la Méthode de Longstaff-Schwartz

## 1. Introduction

La méthode de Longstaff-Schwartz (LS), introduite par Francis Longstaff et Eduardo Schwartz en 2001, représente une avancée majeure en finance quantitative. Elle résout l'un des problèmes les plus complexes du pricing numérique : **la valorisation des options américaines par simulation de Monte Carlo**.

Contrairement aux options européennes, les options américaines peuvent être exercées à tout moment. Cela nécessite de résoudre un problème d'arrêt optimal (Optimal Stopping) en remontant le temps (backward induction). La simulation de Monte Carlo avançant naturellement vers le futur, elle était jugée incompatible avec ce type d'option jusqu'à la méthode LS, qui utilise la **régression par moindres carrés** pour estimer la valeur de continuation.

---

## 2. Équations du Modèle

Le modèle repose sur la dynamique de l'actif sous-jacent et sur l'équation d'évaluation par récurrence arrière (backward induction).

### 2.1 Dynamique du Prix de l'Actif (Cadre Black-Scholes)

Dans ce projet, l'évolution de l'actif sous-jacent suit un Mouvement Brownien Géométrique sous la probabilité risque-neutre $\mathbb{Q}$ :

$$dS_t = (r - q) S_t dt + \sigma S_t dW_t$$

**Description :**
- $S_t$ : Prix de l'actif sous-jacent au temps $t$
- $r$ : Taux d'intérêt sans risque
- $q$ : Taux de dividende continu
- $\sigma$ : Volatilité de l'actif
- $W_t$ : Mouvement brownien standard

### 2.2 Valeur Intrinsèque (Payoff)

Pour un Put américain (cas classique d'exercice anticipé), la valeur d'exercice immédiat est :

$$h(S_t) = \max(K - S_t, 0)$$

### 2.3 Valeur de Continuation (Équation Fondamentale LS)

À un instant $t$, le détenteur de l'option ne l'exerce que si la valeur intrinsèque est supérieure à la valeur de continuation (ce qu'il espère gagner en attendant). La valeur de continuation $C(t, S_t)$ est l'espérance conditionnelle des flux futurs actualisés :

$$C(t, S_t) = \mathbb{E}^\mathbb{Q}[e^{-r \Delta t} V(t+\Delta t, S_{t+\Delta t}) | \mathcal{F}_t]$$

**L'approximation de Longstaff-Schwartz** consiste à projeter cette espérance conditionnelle sur une base de fonctions (ex: Polynômes de Laguerre) :

$$C(t, S_t) \approx \sum_{j=0}^{k} a_j L_j(S_t)$$

---

## 3. Paramètres du Modèle

| Paramètre | Description | Unité | Valeur typique |
|-----------|-------------|-------|----------------|
| **S₀** | Prix spot initial | Monnaie | Varie selon l'actif |
| **K** | Prix d'exercice (Strike) | Monnaie | Proche de S₀ |
| **r** | Taux sans risque | %/an | 1-5% |
| **σ** | Volatilité implicite/historique | %/an | 10-40% |
| **T** | Maturité de l'option | Années | 0.5 - 2 |
| **N** | Nombre de simulations (Trajectoires) | Entier | 10 000 - 100 000 |
| **M** | Nombre de pas de temps | Entier | 252 (jours) |
| **k** | Degré du polynôme de régression | Entier | 2 - 4 |

### 3.1 Interprétation des Paramètres Numériques

#### N (Nombre de Simulations)
- Détermine la précision de la méthode de Monte Carlo (loi des grands nombres).
- L'erreur standard décroît en $1/\sqrt{N}$.

#### M (Nombre de Pas de Temps)
- Représente les points de décision où l'option peut être exercée.
- Plus $M$ est grand, plus on se rapproche d'une option américaine continue (sinon, c'est une option "Bermudéenne").

#### k (Degré du Polynôme de Régression)
- Détermine la flexibilité de la courbe estimant la valeur de continuation.
- $k$ trop faible : sous-apprentissage (biais élevé).
- $k$ trop élevé : sur-apprentissage (overfitting du bruit stochastique).

---

## 4. Propriétés de la Méthode

### 4.1 Backward Induction (Récurrence Arrière)

L'algorithme s'exécute de la maturité $T$ vers $t=0$ :
1. À $t = T$, la valeur de l'option est exactement son payoff : $V(T) = \max(K - S_T, 0)$.
2. Pour chaque instant $t$ précédant, on estime la valeur de continuation via régression.
3. On met à jour le flux de trésorerie (cash-flow) : si le payoff immédiat > valeur de continuation, on exerce (le cash-flow futur devient 0 et est remplacé par le payoff immédiat actualisé).

### 4.2 Régression transversale (Cross-Sectional Regression)

Au lieu de regarder chaque trajectoire isolément, la régression se fait "en coupe" : à un instant $t$ donné, l'algorithme utilise l'ensemble des trajectoires simulées pour estimer la relation entre le prix $S_t$ et les flux futurs.

### 4.3 Filtrage des Trajectoires "In-The-Money" (ITM)

Une règle cruciale de l'algorithme original de Longstaff-Schwartz est de **ne réaliser la régression que sur les trajectoires qui sont "Dans la Monnaie"** (où $h(S_t) > 0$).
- **Pourquoi ?** Si l'option est hors de la monnaie, l'exercice anticipé n'est de toute façon pas optimal. Concentrer la régression sur les trajectoires ITM réduit massivement la variance et améliore le fit des polynômes exactement là où la décision est incertaine.

---

## 5. Avantages et Limitations

### 5.1 Avantages

1. **Scalabilité dimensionnelle** : Contrairement aux arbres binomiaux ou aux différences finies, LS gère très bien les problèmes en grande dimension (options sur paniers d'actifs, options asiatiques).
2. **Flexibilité du sous-jacent** : Peut être couplé à des modèles de dynamique complexes (Heston, sauts, volatilité stochastique) sans modifier l'algorithme de base.
3. **Simplicité d'implémentation** : Repose sur de simples régressions linéaires (Moindres Carrés Ordinaires).

### 5.2 Limitations

1. **Biais par défaut (Lower Bound)** : En raison de l'approximation polynomiale qui est sub-optimale par rapport à la vraie stratégie d'exercice, le prix LS sous-estime légèrement le "vrai" prix américain.
2. **Sensibilité à la base** : Le choix des fonctions de base (Laguerre, Hermite, Monômes simples) et de leur degré influe sur la stabilité des résultats.
3. **Consommation mémoire** : Nécessite de stocker l'intégralité de la matrice des trajectoires ($N \times M$) en mémoire vive pour effectuer la récurrence arrière.

---

## 6. Comparaison avec d'autres Modèles

| Modèle | Type | Avantages | Inconvénients |
|--------|------|-----------|---------------|
| **Arbre Binomial (CRR)** | Treillis | Simple, précis pour 1 actif, sans biais | Malédiction de la dimensionnalité (>2 actifs) |
| **Différences Finies (EDP)**| Grille | Très précis (Greeks faciles) | Inutilisable pour des dimensions > 3 |
| **Longstaff-Schwartz** | Monte Carlo | Parfait pour la grande dimension, très flexible | Demande de la mémoire, donne une borne inférieure |
| **Monte Carlo Standard** | Monte Carlo | Rapide, pricing d'options Européennes | Incapable de pricer l'exercice anticipé (Américain) |

---

## 7. Applications

### 7.1 Pricing d'Options
- Options Américaines standards (Actions, Devises, Commodités)
- Options Bermudéennes (Swaptions, obligations annulables)
- Options Asiatiques avec clause d'exercice anticipé

### 7.2 Finance d'Entreprise
- Évaluation des "Options Réelles" (ex: décision d'investir ou d'abandonner un projet minier à différentes étapes en fonction des cours des matières premières).

---

## 8. Références Bibliographiques

1. **Longstaff, F. A., & Schwartz, E. S. (2001)** - "Valuing American Options by Simulation: A Simple Least-Squares Approach" - *The Review of Financial Studies*

2. **Black, F., & Scholes, M. (1973)** - "The Pricing of Options and Corporate Liabilities" - *Journal of Political Economy*

3. **Glasserman, P. (2003)** - "Monte Carlo Methods in Financial Engineering" - *Springer* (Référence absolue pour l'analyse des biais et de la variance de l'algorithme LS).

---

## 9. Notations Mathématiques

| Symbole | Signification |
|---------|---------------|
| $S_t$ | Prix de l'actif au temps $t$ |
| $r$ | Taux sans risque |
| $q$ | Rendement du dividende |
| $\sigma$ | Volatilité de l'actif |
| $W_t$ | Mouvement brownien |
| $h(S_t)$| Valeur intrinsèque (Payoff) |
| $C(t, S_t)$ | Valeur de continuation espérée |
| $V(t)$ | Valeur de l'option au temps $t$ |
| $L_j(X)$| Polynôme de Laguerre de degré $j$ |
| $\Delta t$| Pas de temps ($T/M$) |

---

## 10. Points Clés à Retenir

1. **Le paradoxe résolu** : LS permet d'utiliser une méthode forward (Monte Carlo) pour résoudre un problème backward (Arrêt optimal).
2. **Moindres carrés** : L'espérance conditionnelle est estimée par une régression transversale sur les prix simulés.
3. **Le filtre ITM** : La régression ne doit s'appliquer que sur les chemins où l'option a une valeur intrinsèque positive, pour éviter d'ajouter du bruit stochastique inutile.
4. **Base de fonctions** : L'utilisation de polynômes orthogonaux (Laguerre) assure une meilleure stabilité numérique que des polynômes simples ($X, X^2, X^3$).
5. **Prime d'exercice anticipé** : Le prix LS sera toujours strictement supérieur ou égal au prix de l'option européenne correspondante (Early Exercise Premium).

---