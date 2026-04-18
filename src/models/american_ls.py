"""
Description : Pricing d'options Américaines par la méthode de Monte Carlo.

Ce module implémente l'algorithme de Longstaff-Schwartz qui utilise une 
régression par moindres carrés (via des polynômes de Laguerre) pour estimer 
la valeur de continuation de l'option et déterminer la frontière d'exercice optimal.

Référence Académique :
- Longstaff, F. A., & Schwartz, E. S. (2001). "Valuing American Options by Simulation: 
  A Simple Least-Squares Approach." The Review of Financial Studies, 14(1), 113-147.
"""

import numpy as np
import numpy.polynomial.laguerre as lag
from typing import Tuple
from src.generators import generate_box_muller

def simulate_paths(
    spot: float,
    volatility: float,
    rate: float,
    dividend: float,
    expiry: float,
    n_simulations: int,
    n_steps: int,
    seed: int = None
) -> np.ndarray:
    """
    Simule les trajectoires du sous-jacent via un Mouvement Brownien Géométrique.
    """
    dt = expiry / n_steps
    paths = np.zeros((n_simulations, n_steps + 1))
    paths[:, 0] = spot
    
    drift = (rate - dividend - 0.5 * volatility**2) * dt
    vol_sqrt_dt = volatility * np.sqrt(dt)
    
    # Pour garantir la reproductibilité sur toute la matrice
    if seed is not None:
        np.random.seed(seed)
        
    for t in range(1, n_steps + 1):
        # On peut appeler generate_box_muller sans seed ici car on a fixé le seed global juste au-dessus
        z = generate_box_muller(n_simulations)
        diffusion = vol_sqrt_dt * z
        paths[:, t] = paths[:, t - 1] * np.exp(drift + diffusion)
        
    return paths

def american_ls_price(
    spot: float,
    strike: float,
    volatility: float,
    rate: float,
    dividend: float,
    expiry: float,
    n_steps: int,
    n_simulations: int,
    degree: int = 3,
    is_put: bool = True,
    itm_only: bool = True,
    seed: int = None
) -> Tuple[float, float, float]:
    """
    Estime le prix d'une option américaine par l'algorithme de Longstaff-Schwartz.

    Retourne
    --------
    Tuple[float, float, float] : (Prix de l'option, Borne basse IC 95%, Borne haute IC 95%)
    """
    dt = expiry / n_steps
    mult = -1.0 if is_put else 1.0
    discount_factor = np.exp(-rate * dt)
    
    # 1. Génération de toutes les trajectoires
    paths = simulate_paths(spot, volatility, rate, dividend, expiry, n_simulations, n_steps, seed)
    
    # 2. Initialisation à la maturité (t = T)
    # Le vecteur V contient les flux de trésorerie (Cash Flows) futurs
    V = np.maximum(mult * (paths[:, n_steps] - strike), 0.0)
    
    # 3. Récurrence Arrière (Backward Induction)
    for t in range(n_steps - 1, 0, -1):
        S_t = paths[:, t]
        
        # Valeur d'Exercice Immédiat (Intrinsic Exercise Value)
        IEV = np.maximum(mult * (S_t - strike), 0.0)
        
        # Identification des trajectoires In-The-Money (ITM)
        itm_indices = np.where(IEV > 0)[0]
        
        # On ne fait la régression que si l'on a suffisamment de chemins ITM
        if len(itm_indices) > degree:
            if itm_only:
                reg_indices = itm_indices
            else:
                reg_indices = np.arange(n_simulations)
                
            # Actualisation des flux futurs d'un pas de temps
            Y = V * discount_factor
            
            # Extraction des données pour la régression
            X_reg = S_t[reg_indices]
            Y_reg = Y[reg_indices]
            
            # Régression Polynomiale de Laguerre
            coeffs = lag.lagfit(X_reg, Y_reg, degree)
            
            # Estimation de la Valeur de Continuation (Continuation Value)
            CV = lag.lagval(S_t, coeffs)
            CV = np.maximum(CV, 0.0) # La valeur de continuation ne peut pas être négative
            
            # Décision d'exercice : on exerce si Exercice Immédiat > Continuation Value ET que l'option est ITM
            exercise_indices = np.where((IEV > CV) & (IEV > 0))[0]
            
            # Mise à jour des Cash Flows
            # Si on exerce, le flux futur devient le payoff immédiat. Sinon, on actualise l'ancien flux.
            V_new = Y.copy()
            V_new[exercise_indices] = IEV[exercise_indices]
            V = V_new
        else:
            # S'il n'y a pas assez de chemins ITM, on se contente d'actualiser
            V = V * discount_factor
            
    # 4. Actualisation finale jusqu'en t=0
    present_values = V * discount_factor
    price = np.mean(present_values)
    
    # 5. Calcul de l'Intervalle de Confiance (IC 95%)
    std_dev = np.std(present_values, ddof=1)
    standard_error = std_dev / np.sqrt(n_simulations)
    ic_lower = price - 1.96 * standard_error
    ic_upper = price + 1.96 * standard_error
    
    return price, ic_lower, ic_upper