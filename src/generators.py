"""
Description : Génération de nombres pseudo-aléatoires pour les simulations de Monte Carlo.

Ce module implémente la transformée de Box-Muller vectorisée pour générer 
des variables aléatoires suivant une loi normale centrée réduite N(0,1) 
à partir d'échantillons de lois uniformes.

Référence Académique :
- Box, G. E. P., & Muller, M. E. (1958). "A Note on the Generation of Random Normal Deviates." 
  Annals of Mathematical Statistics, 29(2), 610-611.
"""

import numpy as np

def generate_box_muller(n_simulations: int, seed: int = None) -> np.ndarray:
    """
    Génère un tableau de nombres aléatoires suivant une loi N(0,1) via Box-Muller.
    
    Paramètres
    ----------
    n_simulations : int
        Le nombre de variables aléatoires normales à générer.
    seed : int, optionnel
        Graine aléatoire pour garantir la reproductibilité des résultats. Par défaut None.
        
    Retourne
    --------
    np.ndarray
        Un tableau numpy 1D contenant `n_simulations` tirages N(0,1).
    """
    # Fixer la graine aléatoire si elle est fournie (Crucial pour la reproductibilité)
    if seed is not None:
        np.random.seed(seed)
        
    # L'algorithme génère des paires de variables, on divise donc par 2
    n_pairs = (n_simulations + 1) // 2
    
    # Génération des variables uniformes U(0,1)
    # On ajoute un très petit epsilon (1e-10) pour éviter le log(0) au cas où np.random.rand() renverrait exactement 0
    u1 = np.maximum(np.random.rand(n_pairs), 1e-10)
    u2 = np.random.rand(n_pairs)
    
    # Transformation de Box-Muller (Vectorisée)
    # Z1 et Z2 sont deux variables normales standards indépendantes
    z1 = np.sqrt(-2.0 * np.log(u1)) * np.cos(2.0 * np.pi * u2)
    z2 = np.sqrt(-2.0 * np.log(u1)) * np.sin(2.0 * np.pi * u2)
    
    # Concaténation des deux tableaux
    z = np.concatenate([z1, z2])
    
    # Si n_simulations est impair, on a généré un nombre de trop, on coupe donc le tableau
    return z[:n_simulations]
