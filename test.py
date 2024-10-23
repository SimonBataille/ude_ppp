import pandas as pd
import matplotlib.pyplot as plt

##
# Charger les données PPP
ppp_data = pd.read_csv('imf-dm-export-20241018.csv', sep=',', header=0, index_col=0)

# Transposer le DataFrame et le reformater
ppp_data = ppp_data.T
ppp_data.reset_index(inplace=True)
ppp_data.columns = ['Year', 'PPP']
#import pdb; pdb.set_trace()

# Convertir 'Year' et 'PPP' en types appropriés
ppp_data['Year'] = ppp_data['Year'].astype(int)
ppp_data['PPP'] = ppp_data['PPP'].astype(float)

# Charger les données USD/JPY
df_usdjpy = pd.read_csv('usdjpy_w.csv')
df_usdjpy['Date'] = pd.to_datetime(df_usdjpy['Date'])
df_usdjpy.set_index('Date', inplace=True)

# Extraire l'année de la date
df_usdjpy['Year'] = df_usdjpy.index.year

# Réinitialiser l'index pour garder 'Date' comme colonne
df_usdjpy.reset_index(inplace=True)

# Convertir le type de 'Year' en int64 pour correspondre à ppp_data
df_usdjpy['Year'] = df_usdjpy['Year'].astype('int64')

# Vérifier les types avant la fusion
# ~ print(f"Type de Year dans df_usdjpy: {df_usdjpy['Year'].dtype}")
# ~ print(f"Type de Year dans ppp_data: {ppp_data['Year'].dtype}")

# Fusionner les deux DataFrames sur 'Year'
df_merged = pd.merge_asof(df_usdjpy.sort_index(), ppp_data.sort_values('Year'), 
                           left_on='Year', right_on='Year', direction='backward')


##
# Calcul de l'écart entre le taux de change et la valeur PPP
df_merged['Abs Var to PPP'] = df_merged['Close'] - df_merged['PPP']

# Calcul de la médiane et de l'écart-type pour centrer les données
median_abs_var = df_merged['Abs Var to PPP'].median()
std_abs_var = df_merged['Abs Var to PPP'].std()
df_merged['Abs Var to PPP Centered'] = df_merged['Abs Var to PPP'] - median_abs_var

# Calculer la moyenne mobile sur 48 observations (approximativement 1 an)
df_merged['Moving Average (1 Year)'] = df_merged['Abs Var to PPP Centered'].rolling(window=48).mean()


##
# Visualisation des écarts centrés
plt.figure(figsize=(10, 6))

# Courbe de l'écart centré
plt.plot(df_merged['Date'], df_merged['Abs Var to PPP Centered'], label='Écart Centré', color='blue')

# Tracer la bande autour de l'écart centré
plt.fill_between(df_merged['Date'], 
                 -std_abs_var, std_abs_var, 
                 color='lightblue', alpha=0.5, label='Intervalle ±1 Écart-Type')
                 
# Tracer la moyenne mobile
plt.plot(df_merged['Date'], df_merged['Moving Average (1 Year)'], label='Moyenne Mobile (1 an)', color='orange', linewidth=2)

# Ligne horizontale à 0
plt.axhline(0, color='gray', linestyle='--', label='Médiane')

# Ajouter des labels et une légende
plt.title("Écart entre la Parité du Pouvoir d'Achat (PPP) et le taux de change JPN/USD")
plt.xlabel("Date")
plt.ylabel("Écart Centré")
plt.legend()
plt.show()
