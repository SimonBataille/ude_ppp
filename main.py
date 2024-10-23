import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Chargement des données de parité de pouvoir d'achat (PPP)
dfPPP = pd.read_csv('imf-dm-export-20241018.csv', sep=',', index_col=0).T
dfPPP.index = dfPPP.index.astype(np.int64)  # Convertir les index (années) en int64

# Chargement des données USD/JPY hebdomadaires
df_usdjpy = pd.read_csv('usdjpy_w.csv')
df_usdjpy['Date'] = pd.to_datetime(df_usdjpy['Date'])
df_usdjpy.set_index('Date', inplace=True)

# Ajouter une colonne `Year` dans `df_usdjpy` pour fusionner par année
df_usdjpy['Year'] = df_usdjpy.index.year.astype(np.int64)  # Convertir Year en int64

# Fusion sur la base de l'année
dfPPP.reset_index(inplace=True)
dfPPP.rename(columns={'index': 'Year'}, inplace=True)

df_usdjpy = pd.merge_asof(df_usdjpy.sort_index(), dfPPP[['Year', 'Japan']].sort_values('Year'), 
                          left_on='Year', right_on='Year', direction='backward')

# Calcul de l'écart absolu entre le taux de change et la valeur PPP
df_usdjpy['Abs Var to PPP'] = df_usdjpy['Close'] - df_usdjpy['Japan']

# Calcul de la médiane et de l'écart-type pour centrer les données
median_abs_var = df_usdjpy['Abs Var to PPP'].median()
std_abs_var = df_usdjpy['Abs Var to PPP'].std()
df_usdjpy['Abs Var to PPP Centered'] = df_usdjpy['Abs Var to PPP'] - median_abs_var

# Affichage des résultats
print(df_usdjpy[['Close', 'Japan', 'Abs Var to PPP', 'Abs Var to PPP Centered']].head())

# Visualisation des écarts centrés et logarithmiques
plt.figure(figsize=(10, 6))

# Courbe de l'écart centré
plt.plot(df_usdjpy.index, df_usdjpy['Abs Var to PPP Centered'], label='Écart Centré', color='blue')
plt.axhline(0, color='gray', linestyle='--')

# Formater l'échelle des dates pour afficher les années
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  # Afficher les années seulement
plt.gca().xaxis.set_major_locator(mdates.YearLocator(5))  # Mettre un intervalle de 5 ans

# Paramétrage du graphique
plt.title('Écart entre USD/JPY et Parité de Pouvoir d\'Achat (PPP)')
plt.xlabel('Date')
plt.ylabel('Écart centré (JPY)')
plt.grid(True)
plt.legend()

# Affichage
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
