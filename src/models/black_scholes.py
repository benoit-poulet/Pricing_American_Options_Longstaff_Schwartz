"""
Description : Pricing d'options Européennes (Formules analytiques et Monte Carlo).

Ce module contient les implémentations pour valoriser des options européennes
standards. Il sert de point de référence (benchmark) pour mesurer la précision
et la prime d'exercice anticipé des options américaines.

Référence Académique :
- Black, F., & Scholes, M. (1973). "The Pricing of Options and Corporate Liabilities."
  Journal of Political Economy, 81(3), 637-654.
"""

import numpy as np
from scipy.special import ndtr
from src.generators import generate_box_muller

def european_analytical_price(
    spot: float,
    strike: float,
    volatility: float,
    rate: float,
    dividend: float,
    expiry: float,
    is_put: bool = True
) -> float:
    """
    Calcule le prix analytique d'une option européenne via la formule de Black-Scholes.

    Paramètres
    ----------
    spot : float : Prix actuel de l'actif (S)
    strike : float : Prix d'exercice (K)
    volatility : float : Volatilité annuelle (sigma)
    rate : float : Taux d'intérêt sans risque (r)
    dividend : float : Taux de dividende annuel (q)
    expiry : float : Maturité en années (T)
    is_put : bool : True pour un Put, False pour un Call (Par défaut True)

    Retourne
    --------
    float : Prix de l'option
    """
    if expiry <= 0:
        return max(0.0, (strike - spot) if is_put else (spot - strike))

    # Calcul des variables d1 et d2
    d1 = (np.log(spot / strike) + (rate - dividend + 0.5 * volatility**2) * expiry) / (volatility * np.sqrt(expiry))
    d2 = d1 - volatility * np.sqrt(expiry)

    # Multiplicateur pour distinguer Call (1) et Put (-1) dans les probabilités
    mult = -1.0 if is_put else 1.0

    nd1 = ndtr(mult * d1)
    nd2 = ndtr(mult * d2)

    # Formule de Black-Scholes avec dividendes (Merton)
    price = mult * (spot * np.exp(-dividend * expiry) * nd1 - strike * np.exp(-rate * expiry) * nd2)
    return price

def european_monte_carlo_price(
    spot: float,
    strike: float,
    volatility: float,
    rate: float,
    dividend: float,
    expiry: float,
    n_simulations: int = 100000,
    is_put: bool = True,
    seed: int = None
) -> float:
    """
    Estime le prix d'une option européenne par simulation de Monte Carlo.

    Paramètres
    ----------
    spot : float : Prix initial
    strike : float : Prix d'exercice
    volatility : float : Volatilité
    rate : float : Taux sans risque
    dividend : float : Taux de dividende
    expiry : float : Maturité
    n_simulations : int : Nombre de trajectoires simulées (Par défaut 100 000)
    is_put : bool : Type d'option
    seed : int : Graine aléatoire pour la reproductibilité

    Retourne
    --------
    float : Estimation du prix par Monte Carlo
    """
    mult = -1.0 if is_put else 1.0
    
    # Paramètres de la dynamique du Mouvement Brownien Géométrique
    drift = (rate - dividend - 0.5 * volatility**2) * expiry
    vol_sqrt_t = volatility * np.sqrt(expiry)

    # Génération des chocs normaux via le module generators
    z = generate_box_muller(n_simulations, seed=seed)
    
    # Simulation des prix finaux à maturité T
    spot_at_t = spot * np.exp(drift + vol_sqrt_t * z)

    # Calcul des payoffs et actualisation au taux sans risque
    payoffs = np.maximum(mult * (spot_at_t - strike), 0.0)
    price = np.exp(-rate * expiry) * np.mean(payoffs)

    return price