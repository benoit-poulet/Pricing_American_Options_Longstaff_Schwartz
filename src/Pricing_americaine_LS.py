import numpy as np
from scipy.special import ndtr
import numpy.polynomial.laguerre as lag
import yfinance as yf

def CallPut (spot, strike, volatility, rate, dividend, expiry, isPut):
    d1 = d2 = 0
    Nd1 = Nd2 = 0
    
    d1 = (np.log(spot/strike) + (rate - dividend + 0.5 * volatility 
                * volatility)* expiry) / (volatility * np.sqrt(expiry))
    d2 = d1 - volatility * np.sqrt(expiry)
    
    if (isPut == "put"):
        mult = -1
    elif(isPut == "call"):
        mult = 1
    else :
        mult = 1
    

    Nd1 = ndtr(mult * d1)
    Nd2 = ndtr(mult * d2)
    
    CallPutPrice = mult * ((spot * np.exp(-dividend * expiry)* Nd1) -
                           (strike * np.exp(-rate * expiry)* Nd2))
    return CallPutPrice

def BoxMuller (nbSimul):
    N_pairs = (nbSimul + 1) // 2
    
    U1 = np.random.rand(N_pairs)
    U2 = np.random.rand(N_pairs)
    
    Z1 = np.sqrt(-2.0 * np.log(U1)) * np.cos(2.0 * np.pi * U2)
    Z2 = np.sqrt(-2.0 * np.log(U1)) * np.sin(2.0 * np.pi * U2)
    
    Z = np.concatenate([Z1, Z2])
    return Z[:nbSimul]

def CallPutMC (S, K, vol, r, div, T, nbSimul, isPut):  
    if (isPut == "put"):
        mult = -1
    elif(isPut == "call"):
        mult = 1
    
    drift = (r - div - 0.5* vol * vol)* T
    vSqrt = vol * np.sqrt(T)
    
    Z = BoxMuller(nbSimul)
    SpotFwdMC = S * np.exp(drift + vSqrt * Z)
    
    payoffMC = np.maximum(mult * (SpotFwdMC - K), 0)
    PriceMC = np.exp(- r * T) * np.mean(payoffMC)
    
    return PriceMC

def SimulPaths (S0, vol, r, div, T, nbSimul, nbPas):
    dt = T / nbPas
    
    Prix = np.zeros((nbSimul, nbPas + 1))
    Prix[:, 0] = S0
    
    drift = (r - div - 0.5* vol * vol)* dt
    
    for t in range (1, nbPas + 1):
        Z = BoxMuller(nbSimul)
        diffusion = vol * np.sqrt(dt) * Z
        Prix[:, t] = Prix[:, t - 1] * np.exp(drift + diffusion)
        
    return Prix
    
def CallPutAmeLS (S0, K, r, div, vol, T, nbPas, nbSimul, degrePoly, isPut, itm):
    dt = T / nbPas
    Prix = SimulPaths(S0, vol, r, div, T, nbSimul, nbPas)
    if (isPut == "put"):
        mult = -1
    elif(isPut == "call"):
        mult = 1
        
    V = np.maximum(mult * (Prix[:, nbPas] - K), 0)
    
    for t in range (nbPas - 1, 0, -1):
        St = Prix[:, t]
        IEV = np.maximum(mult * (St - K), 0)
        indicesITM = np.where(IEV > 0)[0]
        if len(indicesITM) > degrePoly :
            if itm.lower() == "oui" :
                indicesReg = indicesITM
            elif itm.lower() == "non" :
                indicesReg = np.arange(nbSimul)
                
            Y = V * np.exp(- r * dt)
            Yreg = Y[indicesReg]
            StReg = St[indicesReg]
            
            coeffs = lag.lagfit(StReg, Yreg, degrePoly)
            CV = lag.lagval(St, coeffs)
            CV = np.maximum(CV, 0)
            
            indicesExercice = np.where((IEV > CV) & (IEV > 0))[0]
            V[indicesExercice] = IEV[indicesExercice]
            V[V != IEV] = Y[V != IEV]  
        else : 
            V = V * np.exp(- r * dt)
    
    price = np.mean(V) * np.exp(- r * dt)
    
    ecartType = np.std(V * np.exp(- r * dt), ddof=1)
    
    standardError = ecartType / np.sqrt(nbSimul)
    icLower = price - 1.96 * standardError
    icUpper = price + 1.96 * standardError
    
    return price, icLower, icUpper

def dataReelles(ticker):    
    stock = yf.Ticker(ticker)
    try:
        hist = stock.history(period="1y")
        if hist.empty:
            raise ValueError("Aucune donnée trouvée")
        vol = hist['Close'].pct_change().std() * np.sqrt(252) 
        spot = hist['Close'].iloc[-1] 
    except Exception as e:
        print(f"Erreur, utilisation de valeurs par défaut")
        return 100.0, 0.2, 0.0

    div = stock.info.get('dividendRate', None)
    
    if div is not None and spot > 0:
        q = div / spot
    else:
        q = 0.0

    if q > 1: 
        q = q / 100 
    
    print(f"\nDonnées pour {ticker.upper()} ")
    print(f"Spot : {spot:.2f} €")
    print(f"Volatilité : {vol:.4f} ({vol*100:.2f}%)")
    print(f"Dividende : {q:.4f} ({q*100:.2f}%)")
    
    return spot, vol, q

def oatRate(T):
    if T <= 1.0:
        return 0.0212
    elif T <= 2.0:
        return 0.0221
    elif T <= 3.0:
        return 0.0238
    elif T <= 5.0:
        return 0.0268
    elif T <= 7.0:
        return 0.0301
    elif T <= 10.0:
        return 0.0341
    elif T <= 15.0:
        return 0.0382
    else:
        return 0.0410


print ("Bienvenue dans votre pricer d'option Americaines et Européennes")
S0 = float(input("Spot : "))
K = float(input("Strike : "))
r = float(input("Taux sans risque : "))   
div =  float(input("Dividendes : "))
vol = float(input("Volatilité : "))
T = float(input("Maturité : "))
degrePoly = int(input("Degré du Polynôme de régression : ")) 
isPut = input("Call ou Put : ").strip().lower()
itm = input("Trajectoires seulement ITM ? (oui/non) : ").strip().lower()

nbSimul = 100000
nbPas = int(T * 252)

priceEurotheorique = CallPut(S0, K, vol, r, div, T, isPut)
print(f"\nPrix Européen (théorique): {priceEurotheorique:.4f}\n")

priceEuroMC = CallPutMC(S0, K, vol, r, div, T, nbSimul, isPut)
print(f"Prix Européen (Monte Carlo): {priceEuroMC:.4f}\n")

price, lower, upper = CallPutAmeLS(S0, K, r, div, vol, T, nbPas, nbSimul, degrePoly, isPut, itm)

print(f"Prix Américain (LS) : {price:.4f}")
print(f"Intervalle de Confiance (95%) : [{lower:.4f} ; {upper:.4f}]")
print(f"Largeur de l'intervalle : {(upper - lower):.4f}")
print(f"Précision relative : {(upper - lower)/price * 100:.2f}%")

print("\n Impact N (Simulations) ")
for nbTest in [1000, 10000, 100000]:
    p, low, up = CallPutAmeLS(S0, K, r, div, vol, T, nbPas, nbTest, degrePoly, isPut, itm)
    width = up - low
    print(f"N={nbTest:6d} | Prix={p:.4f} | IC : [{low:.4f} ; {up:.4f}] | IC Largeur={width:.4f}")
 

print ("\n\nPRICER D'OPTIONS REELLES ")
#exemples : Total énergies("TTE.PA") ou LVMH ("MC.PA") ou Apple ("AAPL")
ticker = input("Entrez le ticker de votre actif : ").strip().upper()
S0, vol, div = dataReelles(ticker)
isPut = input("\nCall ou Put : ").strip().lower()
K = float(input("Strike : "))
T = float(input("Maturité : "))
r = oatRate(T) 
print(f"Taux oat pour {T} années : {r:.4f}")
degrePoly = int(input("Degré du Polynôme de régression : ")) 
itm = input("Trajectoires seulement ITM ? (oui/non) : ").strip().lower()

priceEurotheorique = CallPut(S0, K, vol, r, div, T, isPut)
print(f"\nPrix Européen (théorique): {priceEurotheorique:.4f}\n")

priceEuroMC = CallPutMC(S0, K, vol, r, div, T, nbSimul, isPut)
print(f"Prix Européen (Monte Carlo): {priceEuroMC:.4f}\n")

price, lower, upper = CallPutAmeLS(S0, K, r, div, vol, T, nbPas, nbSimul, degrePoly, isPut, itm)

print(f"\nPrix Américain (LS) : {price:.4f}")
print(f"Intervalle de Confiance (95%) : [{lower:.4f} ; {upper:.4f}]")
print(f"Largeur de l'intervalle : {(upper - lower):.4f}")
print(f"Précision relative : {(upper - lower)/price * 100:.2f}%")
