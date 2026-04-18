"""
Module : market_data.py
Description : Récupération des données de marché et gestion des taux sans risque.

Ce module utilise l'API yfinance pour récupérer le prix spot, calculer la 
volatilité historique annualisée et extraire le rendement du dividende. 
Il intègre également une fonction d'interpolation en escalier pour la 
courbe des taux OAT (Obligations Assimilables du Trésor) français.
"""

import yfinance as yf
import numpy as np
from typing import Tuple

def fetch_market_data(ticker: str, period: str = "1y") -> Tuple[float, float, float]:
    """
    Récupère les données de marché pour un ticker donné via yfinance.
    
    Paramètres
    ----------
    ticker : str
        Le symbole boursier (ex: 'TTE.PA' pour TotalEnergies, 'AAPL' pour Apple).
    period : str, optionnel
        La période historique pour le calcul de la volatilité. Par défaut "1y".
        
    Retourne
    --------
    Tuple[float, float, float]
        (spot_price, volatilité_annualisée, dividend_yield)
    """
    print(f"Récupération des données pour {ticker.upper()} en cours...")
    stock = yf.Ticker(ticker)
    
    try:
        # 1. Récupération de l'historique
        hist = stock.history(period=period)
        if hist.empty:
            raise ValueError(f"Aucune donnée historique trouvée pour le ticker {ticker}.")
            
        # 2. Prix Spot (Dernier prix de clôture)
        spot = float(hist['Close'].iloc[-1])
        
        # 3. Calcul de la volatilité historique annualisée
        # pct_change() calcule les rendements journaliers, on enlève le premier NaN avec dropna()
        daily_returns = hist['Close'].pct_change().dropna()
        volatility = float(daily_returns.std() * np.sqrt(252))
        
        # 4. Récupération du taux de dividende
        info = stock.info
        # On essaie d'abord de récupérer le 'dividendYield' directement
        dividend = info.get('dividendYield', None)
        
        # Si introuvable, on essaie via le 'dividendRate' divisé par le spot
        if dividend is None:
            div_rate = info.get('dividendRate', None)
            if div_rate is not None and spot > 0:
                dividend = div_rate / spot
            else:
                dividend = 0.0
                
        # Sécurité : Si le dividende est retourné en pourcentage entier (ex: 5 au lieu de 0.05)
        if dividend > 1.0:
            dividend = dividend / 100.0
            
        print(f"Données récupérées avec succès !")
        print(f"   ▶ Spot       : {spot:.2f} €/$")
        print(f"   ▶ Volatilité : {volatility:.4f} ({volatility*100:.2f}%)")
        print(f"   ▶ Dividende  : {dividend:.4f} ({dividend*100:.2f}%)")
        
        return spot, volatility, dividend
        
    except Exception as e:
        print(f"Erreur lors de la récupération des données : {e}")
        print("Utilisation de valeurs par défaut (Spot=100, Vol=20%, Div=0%).")
        return 100.0, 0.20, 0.0


def get_oat_rate(maturity_years: float) -> float:
    """
    Renvoie le taux sans risque basé sur la courbe des taux OAT français.
    Les taux sont interpolés en escalier selon la maturité demandée.
    
    Paramètres
    ----------
    maturity_years : float
        La maturité de l'option en années.
        
    Retourne
    --------
    float
        Le taux sans risque associé.
    """
    if maturity_years <= 1.0:
        return 0.0212  # 2.12%
    elif maturity_years <= 2.0:
        return 0.0221
    elif maturity_years <= 3.0:
        return 0.0238
    elif maturity_years <= 5.0:
        return 0.0268
    elif maturity_years <= 7.0:
        return 0.0301
    elif maturity_years <= 10.0:
        return 0.0341
    elif maturity_years <= 15.0:
        return 0.0382
    else:
        return 0.0410  # 4.10% au-delà de 15 ans