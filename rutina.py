# -*- coding: utf-8 -*-


# %%
from class_post_tratamiento import PostTratamientoTraccion, PostTratamientoFlexibilidad, ComparacionDatos, sensibilidad_anova
import pandas as pd


# Parametros del programa

# Rutas para obtener los parametros mecanicos
enlace_principal_traccion = '' #direccion de los resultados de traccion
enlace_principal_flexibilidad = '' #direccion de los resultados flexibilidad


#ensayo_traccion = PostTratamientoTraccion(enlace_principal_traccion)
#ensayo_flexibilidad = PostTratamientoFlexibilidad(enlace_principal_flexibilidad, 16)

# Archivos con los datos

# Rutas para obtener los resultados mecanicos
resultados_traccion = 'C:/Users/pauline.champion/OneDrive - EURECAT/Documentos/01_Proyecto/03_Pruebas/03_Traccion/resultados_final_traccion.csv'

resultados_flexibilidad = 'C:/Users/pauline.champion/OneDrive - EURECAT/Documentos/01_Proyecto/03_Pruebas/02_Bending/20250422_Flexibility/resultados_final_flex.csv'

# comparacion_traccion = ComparacionDatos(resultados_traccion, 'traccion', enlace_principal_traccion)
# comparacion_flexibilidad = ComparacionDatos(resultados_flexibilidad, 'flexibilidad', enlace_principal_flexibilidad)

# Análisis de sensibilidad 
resultados_final = 'C:/Users/pauline.champion/OneDrive - EURECAT/Documentos/01_Proyecto/03_Pruebas/resultados_final.csv'
df_resultados_final = pd.read_csv(resultados_final, sep=';')

columnas = ['E', 'Re', 'Rm', 'Al', 'Ef', 'Sigma_max', 'Resina', 'Postcurar']
df_resultados_final.columns = columnas

sensibilidad = sensibilidad_anova(columnas, df_resultados_final)
