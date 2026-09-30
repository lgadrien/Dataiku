import dataiku
import pandas as pd
import ast
import json

dataset_activity = dataiku.Dataset("total_user_activity_individual_by_display_name")
df_activity = dataset_activity.get_dataframe()

dataset_matrice = dataiku.Dataset("Matrice_des_droits_1")
df_matrice = dataset_matrice.get_dataframe()

valides_set = set(df_matrice['Group_name'].dropna())

def identifier_groupes_a_supprimer(liste_groupes):
    if isinstance(liste_groupes, str):
        try:
            liste_groupes = ast.literal_eval(liste_groupes)
        except (ValueError, SyntaxError):
            liste_groupes = []
    elif not isinstance(liste_groupes, list):
        liste_groupes = []
            
    groupes_invalides = [str(grp) for grp in liste_groupes if str(grp) not in valides_set]
    groupes_a_supprimer = [grp for grp in groupes_invalides if grp != 'SWIFT']
    
    return groupes_a_supprimer

df_activity['groups_to_remove'] = df_activity['groups'].apply(identifier_groupes_a_supprimer)

df_exclusion = df_activity[df_activity['groups_to_remove'].apply(lambda x: len(x) > 0)].copy()
df_clear_users = df_activity[df_activity['groups_to_remove'].apply(lambda x: len(x) == 0)].copy()

df_exclusion['groups_to_remove'] = df_exclusion['groups_to_remove'].apply(json.dumps)
df_clear_users['groups_to_remove'] = df_clear_users['groups_to_remove'].apply(json.dumps)

dataset_exclusion_out = dataiku.Dataset("exclusion")
dataset_exclusion_out.write_with_schema(df_exclusion)

dataset_clear_users_out = dataiku.Dataset("clear_users")
dataset_clear_users_out.write_with_schema(df_clear_users)