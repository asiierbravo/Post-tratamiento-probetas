# -*- coding: utf-8 -*-


### Codigo para el post-tratamiento de los resultados de los ensayos de tracción

import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np
import os 
from pathlib import Path
from scipy.stats import linregress
import seaborn as sns
import statsmodels.api as sm
from statsmodels.formula.api import ols


def tratar_carpeta(carpeta_principal):
    """Obtener todas las subcarpetas dentro de una carpeta principal.

    Parámetros:
    -----------
        carpeta_principal : str o Path
            Ruta a la carpeta principal.

    Retorna:
    --------
        subcarpeta: lista con subcarpeta
            Lista de rutas a las subcarpetas encontradas.
    """

    # Recoger todas las subcarpetas
    carpetas = Path(carpeta_principal).resolve()
    subcarpeta = [d for d in carpetas.iterdir() if d.is_dir()]

    if not carpetas:
        print("⚠️ no se han encontrado subcarpeta")
    
    return subcarpeta

def tratar_archivos(carpeta, extencion=".xlsx"):
    """Obtener todos los archivos con una extensión específica dentro de una carpeta.

    Parámetros:
    ----------
        carpeta : str o Path
            Ruta de la carpeta a analizar.
        extencion : str
            Extensión de archivo a buscar (por defecto ".xlsx").

    Retorna:
    -------
        archivos: lista con Path
            Lista de archivos encontrados con la extensión dada.
    """

    # Recoger todos los archivos con la extencion dada
    archivos = [f for f in Path(carpeta).glob(f"*{extencion}")]

    # Si nunca archivo encontrado, salir
    if not archivos:
        print(f"⚠️ No se han encontrado archivos en '{carpeta}' con la extencion '{extencion}'")
    
    return archivos

def exportar_datos(df_data, file_name, index=False):
    """Exportar un DataFrame a un archivo CSV con formato europeo.

    Parámetros:
    -----------
        df_data : DataFrame
            Datos a exportar.
        file_name: str
            Ruta y nombre del archivo de salida.
        index : Bool 
            Si se debe incluir el índice en el CSV. Por defecto False.
    """
    df_data.to_csv(file_name, index=index, sep=';', decimal=',', float_format='%.2f')
    print(f"✅ Datos exportados sobre {file_name}")
    
def tratar_datos_final(df, columnas):
    """Reorganizar un DataFrame para agrupar resultados de distintas probetas y tratamientos.

    Parámetros:
    ----------
        df : DataFrame
            Datos crudos con parámetros por columnas.
        columnas : Lista de str
            Lista de nombres de parámetros a considerar.

    Retorna:
    --------
        df_completo: DataFrame
            DataFrame con una fila por probeta y columnas organizadas.
    """
    col = list(df.columns)
    col[0] = 'parametros'
    df.columns = col
    df = df.drop(['Medias', 'Coeficiente de variación', 'Deviación estandar'], axis=1)
    
    numero_parametros = len(columnas)
    columnas_final = columnas + [ "Resina", "Post curar"]
    # Crear un DataFrame nuevo con la estructura deseada 
    
    # Crear el DataFrame final
    final_df = pd.DataFrame(columns=columnas_final)
    df_completo =  pd.DataFrame(columns=columnas_final)
    # Organizar los datos en las columnas correctas
    for j in range(0, int(df.shape[0]/numero_parametros)):
        for i in range(0, int(df.shape[0]/numero_parametros)+1):
            probeta = "probeta_" + str(i + 1)  # Nombre de la probeta
            valores_probeta = df.iloc[numero_parametros*j:numero_parametros*(j+1),
                                      i].values  # Los valores de cada probeta
            manera = df.iloc[numero_parametros*j, 5]
            resina = df.iloc[numero_parametros*j, 6]
            
            nuevas_valores = valores_probeta.T
            nuevas_valores = np.append(nuevas_valores, [resina, manera])
            # Llenamos la nueva tabla
            final_df.loc[probeta] = nuevas_valores
        df_completo = pd.concat([df_completo, final_df], axis=0)
    
    return df_completo

def recoger_medidas(enlace_medidas, hoja, numero_probeta):
    """ Extraer las medidas (ancho y grosor) para una probeta específica desde una hoja 
    de un archivo Excel.

    Parámetros:
    -----------
        enlace_medidas : str o Path
            Ruta al archivo Excel de medidas.
        hoja : str
            Nombre de la hoja donde están los datos.
        numero_probeta : str o int
            Identificador de la probeta.

    Retorna:
    --------
        tuple: float, float
            Ancho y grosor de la probeta.
    """
    df_medidas = pd.read_excel(enlace_medidas, sheet_name=hoja)
    df_medidas.columns = ['probetas', 'ancho', 'grosor']
    df_probeta = df_medidas[df_medidas['probetas'] == numero_probeta]
    ancho =  float(df_probeta['ancho'])
    grosor =  float(df_probeta['grosor'])
    return ancho, grosor


class EnsayoTraccion:
    """Analizar ensayos de tracción a partir de un archivo Excel.

    Parámetros
    ----------
    archivo : str o pathlib.Path
        Ruta del archivo Excel con los datos del ensayo.
    hoja : str, optional
        Nombre de la hoja de cálculo, por defecto 'Hoja1'.
    ancho : float, optional
        Ancho de la probeta, por defecto 50.0 mm.
    grosor : float, optional
        Grosor de la probeta, por defecto 2.0 mm.
    longitud_0_mm : float, optional
        Longitud inicial de referencia para el cálculo de deformaciones, por defecto 100.0 mm.
    save_as : str o None, optional
        Ruta para guardar el gráfico generado.
    plot : bool, optional
        Indica si se debe mostrar el gráfico, por defecto False.
    """
    
    def __init__(self, archivo, hoja='Hoja1', ancho=50.0, grosor=2.0, longitud_0_mm=100.0,
                 save_as=None, plot=False):
        self.archivo = archivo
        self.hoja = hoja
        self.ancho = ancho
        self.grosor = grosor
        self.longitud = longitud_0_mm
        self.save_as= save_as
        self.E = None
        self.Re = None
        self.Rm = None
        self.allongement = None
        self.plot = plot
        self.descargar_datos()
        self.analizar()
        if self.plot:
            self.curva()
        
    
    def descargar_datos(self):
        """Cargar los datos desde un archivo Excel (.xlsx), calcula la tensión y
        renombra las columnas.

        Atributos
        ----------
        df_data : DataFrame
            DataFrame con los datos del Excel
        seccion : float
            Sección de la probeta
        """
        self.df_data = pd.read_excel(self.archivo, sheet_name=self.hoja)
        self.df_data.columns = ['desplacamiento', 'fuerza', 'deformaciones']
        self.seccion = self.ancho * self.grosor
        self.df_data['tensiones'] = self.df_data['fuerza'] / self.seccion
        self.df_data['deformaciones'] = self.df_data['deformaciones']
        print("✅ Datos descargados.")
        
    def modulo_young(self, max_deformacion=0.2):
        """Calcular el módulo de Young (E) en la zona elástica del ensayo.
    
        Parámetros
        ----------
        max_deformacion : float, opcional
            Límite de deformación para considerar la zona elástica (por defecto es 0.2%).
    
        Atributo
        --------
        E : float
            Módulo de Young en MPa.
        """
        zona_elastica = self.df_data[self.df_data['deformaciones'] <= max_deformacion]
        pendiente, _ = np.polyfit(zona_elastica['deformaciones']/100,
                                  zona_elastica['tensiones'], 1)
        self.E = pendiente
    
    def limite_elastique(self, max_deformacion=0.2):
        """Calcular el límite de elasticidad a una deformación específica (0.2%).
    
        Parámetros
        ----------
        max_deformacion : float, opcional
            Valor de deformación para definir el límite elástico (por defecto es 0.2%).
    
        Atributo
        --------
        Re : float
            Límite elástico en MPa.
        """
        limite = self.df_data[self.df_data['deformaciones'] >= max_deformacion].iloc[0]
        self.Re = limite['tensiones']
    
    def resistancia_traccion(self):
        """Calcular la tensión máxima alcanzada durante el ensayo (Rm).
    
        Atributo
        -------
        Rm : float
            Resistencia a la tracción máxima en MPa.
        """
        self.Rm = self.df_data['tensiones'].max()

    def alargamiento_ruptura(self):
        """Calcular el alargamiento relativo a la rotura.
    
        Atributo
        -------
        alargamiento : float
            Alargamiento en valor relativo (por ejemplo, 0.25 para 25%).
        """
        ultimo = self.df_data.iloc[-1]
        self.alargamiento = ultimo['desplacamiento'] / self.longitud

    def analizar(self):
        """Ejecutar todos los análisis del ensayo: módulo de Young, límite elástico,
        resistencia máxima y alargamiento. Imprime los resultados.
        """
        print("\n🔍 Analyse de l'essai :")
        self.modulo_young()
        self.limite_elastique()
        self.resistancia_traccion()
        self.alargamiento_ruptura()
        print(f"📈 Modulo de Young (E)           : {self.E:.2f} MPa")
        print(f"🧱 Limite elasticidad (Re)      : {self.Re:.2f} MPa")
        print(f"🔨 Resistancia a la rotura (Rm) : {self.Rm:.2f} MPa")
        print(f"📏 Alargamiento a la rotura      : {self.alargamiento*100:.2f} %")

    def curva(self):
        """Grafica la curva tensión-deformación del ensayo y guarda el archivo si se 
        especifica.
        """
        plt.figure(figsize=(8, 6))
        plt.plot(self.df_data['deformaciones'], self.df_data['tensiones'],
                 label='Tensión-deformación')
        plt.xlabel('Deformación (%)')
        plt.ylabel('Tensión (MPa)')
        plt.title("Curva ensayo de tracción")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
    # Sauvegarder si le nom de fichier est spécifié
        if self.save_as:
            plt.savefig(self.save_as)
            print(f"✅ Graphique sauvegardé sous {self.save_as}")
            plt.show()
        else:
            plt.show()


class PostTratamientoTraccion():
    """Clase para el post tratamiento de los datos de ensayos de tracción. 

    Esta clase realiza el tratamiento de los archivos de datos de ensayos de tracción, 
    incluyendo la generación de gráficos y el cálculo de medias, desviaciones estándar 
    y coeficientes de variación. Los resultados finales se almacenan en un DataFrame de Pandas.

    Paramétros:
    -----------
    carpeta_principal : str
        Ruta del directorio principal que contiene los archivos de entrada.
    longitud_0_mm : float
        Longitud inicial de la probeta en milímetros (por defecto 45 mm).
    index_traccion : list
        Lista de nombres de las propiedades mecánicas que se calculan.
    
    Atributos:
    ----------
    df_complet : DataFrame
        DataFrame con todos los datos
    """
    def __init__(self, carpeta_principal):
        self.carpeta_principal = carpeta_principal
        self.longitud_0_mm = 45
        self.index_traccion = ['E (MPa)', 'Re (MPa)', 'Rm (MPa)', 'Al (%)']
        self.post_tratamiento_carpeta()

    def post_tratamiento_archivo(self, archivos, export):
        """Realizar el tratamiento de los archivos de ensayos de tracción, incluyendo el 
        cálculo de propiedades mecánicas y la creación de gráficos.
    
        Parámetros:
        -----------
        archivos : list of str
            Lista de rutas de archivos de ensayos de tracción que serán procesados.
        export : str
            Ruta del directorio donde se exportarán los resultados y gráficos.
    
        Retorna:
        --------
        df_final : DataFrame
            DataFrame con los resultados calculados para cada probeta y cada ensayo.
        """
        df_final = pd.DataFrame()
        # Bucle en cada archivo
        for arc in archivos:
            print(f"\n🔍 Tratamiento del archivo : {arc}")
            df_resultados = pd.DataFrame(index=self.index_traccion)
            self.post_curar = []
            resina = []
            hojas = ['1', '2', '3', '4', '5']
            plt.figure(figsize=(8, 6))
            for hoja in hojas:
                print(f"\n🔍 Tratamiento de la hoja : {hoja}")
                # Recoger las medidas de las probetas
                ancho, grosor = recoger_medidas(arc, 'medidas', int(hoja))
                
                # Calcular las caracteristicas mecanicas de las resinas
                prueba = EnsayoTraccion(arc, hoja=hoja, ancho=ancho,
                                       grosor=grosor,
                                       longitud_0_mm=self.longitud_0_mm)
                
                resultados = np.array([prueba.E, prueba.Re, prueba.Rm,
                                       prueba.alargamiento])
                
                df_resultados['probeta_{}'.format(hoja)] = resultados
                
                manera = str(arc).split('\\')[-1].split('.')[0]
                self.post_curar = [manera]*len(resultados)
                numero_resina = str(arc).split('\\')[8]
                resina = [numero_resina]*len(resultados)
                
                plt.plot(prueba.df_data['deformaciones'], prueba.df_data['tensiones'],
                         label='probeta {}'.format(hoja))
            plt.xlabel('Deformación (mm/mm)')
            plt.ylabel('Tensión (MPa)')
            plt.title("Curvas ensayos de tracción para {} {}".format(numero_resina, manera))
            plt.grid(True)
            plt.legend()
            plt.tight_layout()
            
            # Descargar si la ruta esta dada
            save_as = '{}/curvas_traccion_{}_{}.png'.format(export, numero_resina, manera)
            plt.savefig(save_as)
            print(f"✅ Gráfico descargado a {save_as}")
            plt.show()
            
            df_resultados['Medias'] = df_resultados.mean(axis=1)
            df_resultados['Deviación estandar'] = df_resultados.std(axis=1)
            df_resultados['Coeficiente de variación'] = df_resultados['Deviación estandar']/df_resultados['Medias']
            
            df_resultados['Post curar'] = self.post_curar
            df_resultados['Resina'] = resina
            
            df_final = pd.concat([df_final, df_resultados], axis=0)
            
        return df_final
    
    
    def post_tratamiento_carpeta(self):
        """Realizar el tratamiento de los archivos de ensayos de tracción en todos los 
        subdirectorios dentro de la carpeta principal. Los resultados se exportan 
        a archivos CSV y se generan gráficos de los ensayos.
    
        Este método recorre todos los subdirectorios de la carpeta principal, 
        procesa los archivos de ensayos de tracción y guarda los resultados 
        en un archivo CSV y los gráficos generados en las carpetas correspondientes.
    
        No retorna ningún valor, pero guarda los resultados en el sistema de archivos.
        
        Atributos
        ---------
        df_complet : DataFrame
            DataFrame con todos los datos
        """
        
        carpetas = tratar_carpeta(self.carpeta_principal)
        self.df_complet = pd.DataFrame()
        for carpeta in carpetas:
            
            carpeta_export = carpeta/"resultados"
            carpeta_export.mkdir(parents=True, exist_ok=True)
            
            archivos = tratar_archivos(carpeta, extencion=".xlsx")
            df_temp = PostTratamientoTraccion.post_tratamiento_archivo(self, archivos,
                                                                       carpeta_export)
            df_temp.index = self.index_traccion*len(self.post_curar)
            carpeta_nombre = str(carpeta).split('\\')[8]
            
            exportar_datos(df_temp, '{}/resultados_{}.csv'.format(
                carpeta_export, carpeta_nombre), index=True)
            
            df_temp_T = tratar_datos_final(df_temp, self.index_traccion)
            
            self.df_complet = pd.concat([self.df_complet, df_temp_T], axis=0)
        
        exportar_datos(self.df_complet, '{}/resultados_final_traccion.csv'.format(
            self.carpeta_principal), index=True) 


        
class EnsayoFlexibilidad:
    """Clase para procesar los resultados de los ensayos de flexibilidad.

    Esta clase permite cargar los datos de un archivo Excel, procesarlos, calcular 
    el esfuerzo máximo y el módulo de elasticidad para cada probeta, y graficar los 
    resultados. También puede guardar los gráficos generados en un archivo.

    Atributos
    ---------
    archivo : str
        Ruta del archivo Excel que contiene los datos del ensayo.
    resina : str
        Tipo de resina utilizada en el ensayo.
    hoja : str, opcional
        Nombre de la hoja del archivo Excel que contiene los datos (por defecto es 'Hoja1').
    longitud_apoyo : float, opcional
        Longitud de apoyo de la probeta en el ensayo (por defecto es 16 mm).
    save_as : str, opcional
        Ruta para guardar los gráficos generados (por defecto es None, lo que no guarda los gráficos).
    plot : bool, opcional
        Indica si se deben mostrar los gráficos (por defecto es False).
    
    Atributos
    ---------
    df_flex : pd.DataFrame
        DataFrame que contiene los datos del ensayo de flexibilidad cargados desde el archivo.
    indices_probetas : list
        Lista de índices de las probetas encontradas en los datos.
    F : np.ndarray
        Fuerza aplicada en cada probeta.
    d : np.ndarray
        Desplazamiento de cada probeta.
    sigma : np.ndarray
        Esfuerzo calculado para cada probeta.
    epsilon : np.ndarray
        Deformación calculada para cada probeta.
    df_resultados : pd.DataFrame
        DataFrame con los resultados de los cálculos, incluyendo esfuerzo máximo y módulo de elasticidad.
    """
    def __init__(self, archivo, resina, hoja='Hoja1', longitud_apoyo=16, save_as=None,
                 plot=False):
        self.archivo = archivo
        self.resina = resina
        self.hoja = hoja
        self.longitud_apoyo = longitud_apoyo
        self.save_as= save_as
        # Determinar el nombre de la columna según el tipo de hoja
        if self.hoja == 'Sin curar':
            self.nombre_columna ='SC'
        elif self.hoja == 'Microondas':
            self.nombre_columna ='MO'
        elif self.hoja == 'Luz':
            self.nombre_columna ='Luz'
        elif self.hoja == 'Luz + Calor':
            self.nombre_columna ='LC'
        else:
            print('Hay un problema con el nombre de la hoja')
            
        self.plot = plot
        self.descargar_datos()
        self.analizar_datos()
    
    def descargar_datos(self):
        """Cargar los datos del archivo Excel y extrae los índices de las probetas.

        Esta función lee los datos de la hoja especificada y obtiene los índices de las 
        probetas correspondientes al tipo de resina y la hoja seleccionada.
        
        Atributos
        ---------
        df_flex : pd.DataFrame
            DataFrame que contiene los datos del ensayo de flexibilidad cargados desde el
            archivo.
        indices_probetas : list
            Lista de índices de las probetas encontradas en los datos.
        """
        #Cargar datos desde Excel
        self.df_flex = pd.read_excel(self.archivo, sheet_name=self.hoja)
        
        
        # === Identificar las filas donde empiezan las probetas ===
        self.indices_probetas = [col.split('-')[-1] for col in self.df_flex.columns if
                                 f'{self.resina}MF-{self.nombre_columna}-' in col]
        
        # Asumiendo que las columnas se llaman 'Fuerza' y 'Desplazamiento'

    def analizar_datos(self):
        """Procesar los datos de flexibilidad, calcula el esfuerzo, la deformación y el
        módulo de elasticidad.

        Esta función recorre las probetas disponibles en los datos, calcula el esfuerzo 
        máximo,
        la deformación, el módulo de elasticidad y genera gráficos de los resultados.

        Los resultados incluyen:
        - Esfuerzo máximo (MPa)
        - Módulo de elasticidad (MPa)
        
        También se genera una visualización de los gráficos de la fuerza vs. desplazamiento 
        (F vs d)
        y esfuerzo vs. deformación (σ vs ε).

        Si `plot` es `True`, los gráficos se muestran. Si `save_as` está definido, se 
        guardan.
        
        Atributos
        ---------
        F : np.ndarray
            Fuerza aplicada en cada probeta.
        d : np.ndarray
            Desplazamiento de cada probeta.
        sigma : np.ndarray
            Esfuerzo calculado para cada probeta.
        epsilon : np.ndarray
            Deformación calculada para cada probeta.
        df_resultados : pd.DataFrame
            DataFrame con los resultados de los cálculos, incluyendo esfuerzo máximo y módulo de elasticidad.
        """
        resultados = []
        plt.figure(figsize=(10, 4))
        for probeta in range(int(len(self.indices_probetas)/3)):
            
            print(f"\n🔍 Traitement de la feuille : {self.hoja} {probeta}")
            numero_probeta = self.nombre_columna + self.indices_probetas[3*probeta]
            ancho, grosor = recoger_medidas(self.archivo, 'medidas', numero_probeta)
            
            # Definir las columnas de Fuerza y Desplazamiento para la probeta actual
            col_f = f"{self.resina}MF-{self.nombre_columna}-{self.indices_probetas[3*probeta]}"
            col_d = f"{self.resina}MF-{self.nombre_columna}-{self.indices_probetas[3*probeta+1]}"
            
            if col_f not in self.df_flex or col_d not in self.df_flex:
                continue  # Saltar si faltan columnas
            
            self.F = self.df_flex[col_f].dropna()
            self.d = self.df_flex[col_d].dropna()
            
            # Alinear tamaños
            min_len = np.where(self.d == 5)[0][-1]
            # self.F = np.array(self.F[:min_len])[1:]/10
            # self.d = np.array(self.d[:min_len])[1:]
            self.F = np.array(self.F[:min_len])[1:]/10
            self.d = np.array(self.d[:min_len])[1:]
            
            
            # Calcular esfuerzo y deformación
            self.sigma = (3 *  self.F *  self.longitud_apoyo) / (2 *  ancho *  grosor**2)
            self.epsilon = (6 *  grosor *  self.d) / ( self.longitud_apoyo**2)
        
            # Calcular módulo de elasticidad (en rango lineal)
            lineal_range = np.where(self.d == 0.1)[0][-1]
            pendiente, _ = np.polyfit(list(self.epsilon[:lineal_range]), 
                                  list(self.sigma[:lineal_range]), 1)
            E_flexion = pendiente
            sigma_max =  self.sigma.max()
        
            resultados.append({
                "Probeta": probeta+1,
                "E_flexion (MPa)": round(E_flexion, 2),
                "Esfuerzo máximo (MPa)": round(sigma_max, 2)
            })
            
            #Generar gráficos
            plt.subplot(1, 2, 1)
            plt.plot(self.d,
                     self.F,
                     label='Probeta {}'.format(probeta+1))
            plt.xlabel('Distancia (mm)')
            plt.ylabel('Fuerza (N)')
            plt.title(f'F vs d para {self.resina} {self.hoja}')
            plt.legend()
            plt.grid(True)
         
            plt.subplot(1, 2, 2)
            plt.plot(self.epsilon,
                     self.sigma,
                     label='Probeta {}'.format(probeta+1))
            plt.xlabel('Deformación (ε)')
            plt.ylabel('Esfuerzo (MPa)')
            plt.title(f'σ vs ε para {self.resina} {self.hoja}')
            plt.legend()
            plt.grid(True)
     
        plt.tight_layout()
        # Guardar el gráfico si se especifica
        if self.save_as:
            plt.savefig(self.save_as)
            plt.show()
        else:
            plt.show()

        self.df_resultados = pd.DataFrame(resultados)


class PostTratamientoFlexibilidad():
    """Clase para realizar el post-tratamiento de los ensayos de flexibilidad.

    Esta clase procesa los archivos de ensayos de flexibilidad, genera gráficos de los
    resultados, calcula estadísticas como medias, desviaciones estándar y coeficientes de
    variación, y exporta
    los resultados a archivos CSV.

    Atributos
    ---------
    carpeta_principal : str
        Ruta del directorio principal que contiene los archivos de los ensayos.
    longitud_apoyo : float
        Longitud de apoyo de la probeta durante el ensayo de flexibilidad.
    index_flexibilidad : list
        Lista de los índices para las propiedades calculadas, como el módulo de
        flexibilidad y el esfuerzo máximo.
    post_curar_flex : list
        Lista de los diferentes tipos de post-tratamiento (hojas) a considerar en el
        análisis.
    df_complet : pd.DataFrame
        DataFrame con los resultados finales del análisis de todos los archivos.
    """
    def __init__(self, carpeta_principal, longitud_apoyo):
        self.carpeta_principal = carpeta_principal
        self.longitud_apoyo = longitud_apoyo
        self.index_flexibilidad = ['Modulo de Flexibilidad (E_f)',
                                   'Esfuerzo max (Sigma_max)']
        self.post_curar_flex = ['Sin curar', 'Microondas', 'Luz', 'Luz + Calor']
        self.post_tratamiento_carpeta_flex()
    
    def post_tratamiento_archivo_flex(self, archivo, export):
        """Procesar un archivo de ensayo de flexibilidad y calcula las estadísticas
        correspondientes.

        Este método analiza los datos de cada ensayo en el archivo, genera los gráficos de
        los resultados, y calcula las medias, desviaciones estándar y coeficientes de
        variación de los datos obtenidos.

        Parámetros
        ----------
        archivo : str
            Ruta del archivo Excel que contiene los datos de los ensayos de flexibilidad.
        export : str
            Ruta donde se deben guardar los gráficos generados.

        Retorna
        -------
        df_final : DataFrame
            DataFrame con los resultados procesados de los ensayos, incluyendo el módulo
            de flexibilidad y el esfuerzo máximo, además de las estadísticas calculadas
            (medias, desviaciones estándar, etc.).
        """
        df_final = pd.DataFrame()
        # Bucle para procesar cada hoja (tipo de post-tratamiento)
        for hoja in self.post_curar_flex:
            df_resultados_flex = pd.DataFrame(index=self.index_flexibilidad)
            plt.figure(figsize=(8, 6))
           
            numero_resina = str(archivo).split('\\')[9]
            save_as = '{}/curvas_flexibilidad_{}_{}.png'.format(export, numero_resina,
                                                                hoja)

            prueba = EnsayoFlexibilidad(archivo, numero_resina, hoja=hoja,
                                   longitud_apoyo=self.longitud_apoyo, save_as=save_as)
                
            df_resultados_flex = prueba.df_resultados.T
            df_resultados_flex = df_resultados_flex.drop(['Probeta'], axis=0)

            # Guardar gráfico si es necesario
            print(f"✅ Gráfico descargado a {save_as}")

            # Calcular estadísticas 
            df_resultados_flex['Medias'] = df_resultados_flex.mean(axis=1)
            df_resultados_flex['Deviación estandar'] = df_resultados_flex.std(axis=1)
            df_resultados_flex['Coeficiente de variación'] = df_resultados_flex['Deviación estandar']/df_resultados_flex['Medias']
            
            df_resultados_flex['Post curar'] = [hoja]*df_resultados_flex.shape[0]
            df_resultados_flex['Resina'] = [numero_resina]*df_resultados_flex.shape[0]
            
            df_final = pd.concat([df_final, df_resultados_flex], axis=0)
            
        return df_final

    def post_tratamiento_carpeta_flex(self):
        """Procesar todos los archivos en la carpeta principal y genera los resultados
        finales de flexibilidad.

        Este método recorre todos los archivos en la carpeta principal, procesa cada uno
        utilizando el método `post_tratamiento_archivo_flex`, y exporta los resultados de
        cada archivo a un archivo CSV.
        Además, guarda los resultados agregados en un archivo CSV final.

        Los gráficos de cada archivo se guardan en subcarpetas dentro de cada carpeta
        correspondiente.
        
        Atributos:
        ----------
            df_complet : pd.DataFrame
                DataFrame con los resultados finales del análisis de todos los archivos.
        """
        carpetas = tratar_carpeta(self.carpeta_principal)
        self.df_complet = pd.DataFrame()
        # Procesar cada carpeta de ensayo
        for carpeta in carpetas:
            
            carpeta_export = carpeta/"resultados"
            carpeta_export.mkdir(parents=True, exist_ok=True)
            
            archivo = tratar_archivos(carpeta, extencion=".xlsx")[0]
            # Obtener los resultados procesados para cada archivo
            df_temp = PostTratamientoFlexibilidad.post_tratamiento_archivo_flex(self,
                                                                                archivo,
                                                                                carpeta_export)
            
            df_temp.index = self.index_flexibilidad*len(self.post_curar_flex)
            
            carpeta_nombre = str(carpeta).split('\\')[9]
            
            # Exportar resultados a CSV
            exportar_datos(df_temp, '{}/resultados_flex_{}.csv'.format(
                carpeta_export, carpeta_nombre), index=True)
            
            # Transponer los datos y agregar a los resultados finales
            df_temp_T = tratar_datos_final(df_temp, self.index_flexibilidad)
            
            self.df_complet = pd.concat([self.df_complet, df_temp_T], axis=0)
        
        # Exportar todos los resultados finales a un archivo CSV
        exportar_datos(self.df_complet, '{}/resultados_final_flex.csv'.format(
            self.carpeta_principal), index=True) 
        

class ComparacionDatos():
    """Clase para comparar datos de diferentes ensayos y visualizarlos en gráficos.

    Esta clase se encarga de cargar un archivo CSV con los resultados de las pruebas, 
    realizar algunos cálculos como medias y máximos, y generar gráficos de dispersión 
    y diagramas de barras para visualizar la comparación entre diferentes parámetros de
    las pruebas.

    Atributos
    ---------
    archivo : str
        Ruta del archivo CSV con los datos de las pruebas.
    prueba : str
        Tipo de prueba, utilizado para determinar cómo se deben graficar los datos. 
        Puede ser 'flexibilidad' o cualquier otro tipo de prueba.
    save_as : str, opcional
        Ruta donde guardar las figuras generadas. Si no se proporciona, los gráficos se 
        mostrarán sin guardarse.
    """
    def __init__(self, archivo, prueba, save_as=None):
        self.archivo = archivo
        self.prueba = prueba
        self.save_as =save_as
        self.descargar_datos()
        self.cambiar_datos()
        self.medias()
        self.maximum()
        self.plot_todos_datos()
        self.barplot_datos()

    def descargar_datos(self):
        """Cargar los datos desde el archivo CSV especificado.

        El archivo debe estar en formato CSV con separador ';' y decimal ','.
        
        Atributo
        --------
        df : DataFrame
        """
        self.df = pd.read_csv(self.archivo, sep=';', decimal=',')

    def cambiar_datos(self):
        """Realizar modificaciones en los datos cargados, como renombrar columnas y
        convertir valores numéricos.

        La primera columna de los datos se renombra a 'Probetas' y se elimina.
        Luego, se convierte cada parámetro en tipo numérico para el análisis posterior.
        
        Atributos
        ---------
        col : lista str
            Lista de nombre de columnas
        df : DataFrme
            DataFrame con los datos a graficar
        col_param : lista de str
            Lista de caracteristicas mecanicas
        nuevo_df : DataFrame
            DataFrame con los datos y los nuevos nombres de columnas
            
        """
        self.col = list(self.df)
        self.col[0] = 'Probetas'
        self.df.columns = self.col
        self.df = self.df.drop(['Probetas'], axis=1)
        self.col_param = self.col[1:-2]
        conv =[]
        self.nuevo_df = pd.DataFrame()
        for elem in self.col_param :
            conv = pd.to_numeric(self.df[elem])
            conv_df = pd.DataFrame(conv)
            self.nuevo_df = pd.concat([self.nuevo_df, conv_df], axis=1)
        self.nuevo_df = pd.concat([self.nuevo_df, self.df[self.col[-2:]]], axis=1)

    def medias(self):
        """Calcular las medias de los parámetros agrupados por resina y tipo de curado.

        Los resultados se almacenan en `self.df_medias`.
        """
        self.df_medias = self.nuevo_df.groupby(self.col[-2:]).mean()
    
    def maximum(self):
        """Calcular los valores máximos de los parámetros agrupados por resina y tipo de curado.

        Los resultados se almacenan en `self.df_max`.
        """
        self.df_max = self.nuevo_df.groupby(self.col[-2:]).max()

    def plot_todos_datos(self):
        """Generar un gráfico de dispersión (scatter plot) para comparar todos los datos
        de las pruebas.

        Si el tipo de prueba es 'flexibilidad', se genera un único gráfico.
        Si es otro tipo de prueba, se generan varios gráficos de dispersión comparando
        diferentes parámetros.

        El gráfico se guarda en la ruta especificada por `self.save_as` si se proporciona, 
        o se muestra directamente en pantalla si no se especifica.
        """
        if self.prueba == 'flexibilidad':
            sns.scatterplot(data=self.nuevo_df, x=self.col[1], y=self.col[2],
                            hue="Resina", style="Post curar")
            plt.title('Comparación entre todos los datos de las pruebas de {}'.format(self.prueba))
        else:
           
            fig, axes = plt.subplots(3, 3, figsize=(13, 9))
            fig.suptitle('Comparación entre todos los datos de las pruebas de {}'.format(self.prueba))
            ax = [axes[0, 0], axes[0, 1], axes[0, 2], axes[1, 0], axes[1, 1], axes[1, 2],
                  axes[2, 0], axes[2, 1], axes[2,2]]
            
            sns.scatterplot(data=self.nuevo_df, x=self.col[1], y=self.col[2],
                            hue="Resina", style="Post curar", legend=False, ax=ax[0])

            sns.scatterplot(data=self.nuevo_df, x=self.col[1], y=self.col[3],
                            hue="Resina", style="Post curar", legend=False, ax=ax[3])

            sns.scatterplot(data=self.nuevo_df, x=self.col[1], y=self.col[4],
                            hue="Resina", style="Post curar", legend=False, ax=ax[6])

            sns.scatterplot(data=self.nuevo_df, x=self.col[2], y=self.col[3],
                            hue="Resina", style="Post curar", legend=False, ax=ax[1])

            sns.scatterplot(data=self.nuevo_df, x=self.col[2], y=self.col[4],
                            hue="Resina", style="Post curar", legend=False, ax=ax[4])

            sns.scatterplot(data=self.nuevo_df, x=self.col[3], y=self.col[4],
                            hue="Resina", style="Post curar", ax=ax[2])
        plt.legend(loc='center right', bbox_to_anchor=(1, 0.5))
        plt.tight_layout()
        if self.save_as:
            export = self.save_as + '/comparacion_datos_{}_scatterplot.png'.format(self.prueba)
            plt.savefig(export)
            plt.show()
        else:
            plt.show()
           
    def barplot_datos(self):
        """Generar un diagrama de barras (barplot) para comparar los datos de las pruebas.

        Si el tipo de prueba es 'flexibilidad', se genera un gráfico con dos barras.
        Si es otro tipo de prueba, se generan varios gráficos comparando diferentes
        parámetros.

        El gráfico se guarda en la ruta especificada por `self.save_as` si se proporciona, 
        o se muestra directamente en pantalla si no se especifica.
        """
        if self.prueba == 'flexibilidad':
            fig, axes = plt.subplots(1, 2, figsize=(13, 9))
            ax = [axes[0], axes[1]]
        else:
            fig, axes = plt.subplots(2, 2, figsize=(13, 9))
            ax = [axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]]
        fig.suptitle('Comparación entre todos los datos de las pruebas de {}'.format(self.prueba))
        k = 0
        for param in self.col_param:
            if k == 3:
                sns.barplot(self.nuevo_df, x="Resina", y=param, hue="Post curar", ax=ax[k])
            else:
                sns.barplot(self.nuevo_df, x="Resina", y=param, hue="Post curar",
                            legend=False, ax=ax[k])
            k+=1
        plt.legend(loc='center right', bbox_to_anchor=(1.3, 1))
        plt.tight_layout()
        if self.save_as:
            export = self.save_as + '/comparacion_datos_{}_barplot.png'.format(self.prueba)
            plt.savefig(export)
            plt.show()
        else:
            plt.show()
            

def sensibilidad_anova(col, df_final):
    """Calcular los índices de sensibilidad ANOVA de tipo II para múltiples variables de
    salida en función de los factores categóricos 'Resina' y 'Postcurar'.

    Parametros
    ----------
    col : lista de str
        Lista con los nombres de las columnas del DataFrame. Las columnas de salida se
        extraen usando `col[1:-2]`, asumiendo que las variables de salida están en esa posición.
    df_final : DataFrame
        DataFrame que contiene tanto las variables de entrada ('Resina', 'Postcurar') como
        las variables de salida numéricas.

    Retorna
    -------
    anova_final : DataFrame
        Un DataFrame que contiene los resultados del análisis ANOVA para cada variable de salida.
        Cada fila representa un factor ('Resina' o 'Postcurar') y su influencia sobre una salida,
        incluyendo el estadístico F, valor p, suma de cuadrados y grados de libertad, junto con
        una columna adicional que indica a qué salida pertenece cada resultado.
    """
    anova_final = pd.DataFrame()    
    for output in col[1:-2]:
        formula = f"{output} ~ C(Resina) + C(Postcurar)"
        model = ols(formula, data=df_final).fit()
        anova_result = sm.stats.anova_lm(model, typ=2)
        parametros = pd.DataFrame([output]*3, columns=['Salida'], index=anova_result.index)
        anova_result = pd.concat([anova_result, parametros], axis=1)
        anova_final = pd.concat([anova_final, anova_result], axis=0)
    return anova_final
