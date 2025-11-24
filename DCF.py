#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#--------------------------------------------------------Importation des bibliotheque------------------------------------------------------

import itertools #bibliotheque pour les combinaisons
import pandas as pd #bibliotheque manipulation de données
import matplotlib.pyplot as plt #bilbiotheque graphique

#--------------------------------------------------------FONCTIONS-------------------------------------------------------------------------

def dcf_valuation(fcf_list, discount_rate, growth_rate_terminal):
    
    if discount_rate <= growth_rate_terminal:
        return None  #Retourne None si erreur

    #Etape 3 : Calcul de la Valeur Terminale (discounted_TV)
    FCF_n_plus_1 = fcf_list[-1] * (1 + growth_rate_terminal)
    
    n = len(fcf_list) #nombre d'années
    total_discounted_fcf = 0.0 #initialisation de la variable
    
    TVn = FCF_n_plus_1 / (discount_rate - growth_rate_terminal)# Gordon-Shapiro
    
    discounted_TV = TVn / (1 + discount_rate) ** n
    
    #Etape 4 : Actualisation des FCF (total_discounted_fcf)
    for i, FCF_n in enumerate(fcf_list): #i est l'index
        
        discounted_fcf_n = FCF_n / (1 + discount_rate) ** (i+1)
        
        total_discounted_fcf += discounted_fcf_n
        
    #Etape 5 : Valeur d'Entreprise
    total_value = total_discounted_fcf + discounted_TV
    return total_value

#--------------------------------------------------------Initialisation des données------------------------------------------------------
print("\n" + "="*70)
print("Lancement du code...")

#Etape 1 : Projection des FCF(Liste des listes)
fcf_scenarios = [
    [8, 10, 12],     # FCF Très Faibles
    [10, 12, 15],    # FCF Faibles
    [12, 15, 18],    # FCF Moyens
    [15, 18, 22]     # FCF Élevés
]

# Etape 2 : Taux d'actualisation (WACC) et taux de croissance terminale (g)
discount_rates = [0.08, 0.09, 0.10, 0.11, 0.12]
growth_rates = [0.02, 0.03]

#--------------------------------------------------------Calcul des 40 modélisations-----------------------------------------------------
all_dcf_results = []
scenario_counter = 1

for fcf_list, r, g in itertools.product(fcf_scenarios, discount_rates, growth_rates):
    
    # Appel de la fonction pour chaque scénario
    VE = dcf_valuation(fcf_list, r, g)
    
    # Stockage et affichage du résultat
    if VE is not None:
        
        #Stocke le résultat final (VE)
        all_dcf_results.append({
            "Scenario_ID": scenario_counter,
            "FCF_List": fcf_list,
            "Discount_Rate": r,
            "Growth_Rate": g,
            "VE_Result": VE
        })
        
    scenario_counter += 1

#--------------------------------------------------------Visualisation-------------------------------------------------------------------
df_results = pd.DataFrame(all_dcf_results)

# 1. Création et Catégorisation de FCF_Type (pour l'ordre logique du graphique)
fcf_map = {
    str([8, 10, 12]): 'Très Faible',
    str([10, 12, 15]): 'Faible',
    str([12, 15, 18]): 'Moyen',
    str([15, 18, 22]): 'Élevé'
}
df_results['FCF_Type'] = df_results['FCF_List'].astype(str).map(fcf_map)

# Définir l'ordre catégoriel pour la légende
fcf_order = ['Très Faible', 'Faible', 'Moyen', 'Élevé']
df_results['FCF_Type'] = pd.Categorical(
    df_results['FCF_Type'],
    categories=fcf_order,
    ordered=True
)

# 2. Création de la colonne de légende complète
df_results['Legende'] = df_results['FCF_Type'].astype(str) + " (g=" + (df_results['Growth_Rate'] * 100).round(0).astype(int).astype(str) + "%)"

# 3. Création du Graphique en Lignes Unique (Méthode robuste)
fig, ax = plt.subplots(figsize=(12, 8)) # Crée la figure (fig) et l'axe (ax)

# Tracer toutes les lignes en itérant sur les groupes (sort=False préserve l'ordre catégoriel)
for name, group in df_results.groupby('Legende', sort=False):
    group.plot(
        x='Discount_Rate',
        y='VE_Result',
        ax=ax,
        marker='o',
        label=name,
        legend=False
    )

# 4. Configuration
ax.set_title("Analyse de Sensibilité DCF : VE en fonction du Taux d'Actualisation")
ax.set_xlabel("Taux d'Actualisation (r)")
ax.set_ylabel("Valeur d'Entreprise (VE) en millions")

# Configuration de la Légende (utilise les handles pour garantir l'ordre)
handles, labels = ax.get_legend_handles_labels()
ax.legend(
    handles, labels, title='Scénario FCF & Croissance', loc='center right', bbox_to_anchor=(1.35, 0.5)
)

ax.grid(True, linestyle='--', alpha=0.7)
ax.set_xticks(df_results['Discount_Rate'].unique())
ax.ticklabel_format(style='plain', axis='y')

# SAUVEGARDE DU GRAPHIQUE (Méthode la plus fiable)
fig.tight_layout(rect=[0, 0, 1, 1]) # Assure que la mise en page est correcte pour la sauvegarde
fig.canvas.draw() # Force le rendu du graphique en mémoire

plt.savefig("Analyse_DCF_Sensibilite.png", dpi=300, bbox_inches='tight')
plt.close(fig) # Fermer la figure pour libérer les ressources

print("✅ Succès : Le graphique a été sauvegardé dans Analyse_DCF_Sensibilite.png")
print("="*70)
