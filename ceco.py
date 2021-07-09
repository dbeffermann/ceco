import streamlit as st
import pandas as pd
import base64
import re

regex_codigo = r'(?<={\s)(.*)(?=\s})'
regex_empresa = r'(?<=}\s)([A-Z]+?\s[A-Z]+)(?=\s)|(?<=}\s)([A-Z]+)(?=\s)'
regex_año = r'20\d{2}'

regex_ceco_inicio = r'^\d+\s\(\s+\)'
regex_ceco_fin = r'Total\s\(\d+\s\(\s+\)\)'

def si(a,b):
    """Recibe dos parametros, si el primero tiene largo 0, devolverá el segundo"""
    
    if len(a) > 0:
        return a
    else:
        return b
    
def rellenar(df, colname):
    """Función auxiliar, es genérica para arrastrar los valores no nulos de una columna"""
    df_tmp = df.copy()
    value = '-'
    for index, row in df_tmp.iterrows():

        if row[colname] != '-':
            value = row[colname]

        row[colname] = value
    return df_tmp

def proceso(archivo):
    """Función principal para procesar los archivos"""
    
    df = pd.read_excel(archivo, engine = 'openpyxl', skiprows = 1).iloc[:-1].fillna('-')
    df.columns = [str(i) for i in df.columns]

    ceco_idx = [x for x,y in df.iterrows() if re.findall(inicio, y['Centro de costo'])]
    ceco_idx.append(df.shape[0])
    df_list = [df.iloc[ceco_idx[n-1]:ceco_idx[n]-1].assign(Ceco = re.findall(r'\d+', df['Centro de costo'].iloc[ceco_idx[n-1]])[0]) for n in range(1, len(ceco_idx))]

    #df_list.append(df.iloc[ceco_idx[-1]:df.shape[0]-1])


    df_acum = pd.DataFrame()
    for df_iter in df_list:

        df_out = df_iter.iloc[::-1]
        for i in df_iter.columns[:-3]:

            df_out = rellenar(df_out, i)
        df_acum = df_acum.append(df_out).iloc[::-1]
    df_acum = df_acum[df_acum['Descripcion del Recurso'] != '-']
    
    #Extraccion de atributos de la columna Activos.
    df_acum['Codigo'] = df_acum['Activos'].apply(lambda x: si(re.findall(regex_codigo, x), [''])[0])
    df_acum['Año'] = df_acum['Activos'].apply(lambda x: si(re.findall(regex_año, x), [''])[0])
    df_acum['Empresa'] = df_acum['Activos'].apply(lambda x: si([i for i in si(re.findall(regex_empresa, x), [''])[0] if len(i)>0],[''])[0])

    return df_acum

###########
archivo = st.file_uploader('Subir archivo')

if archivo:
    df = proceso(archivo)
    csv = df.to_csv(index=False, sep=',', encoding = 'latin1')
    b64 = base64.b64encode(csv.encode('latin1')).decode()
    st.markdown(f'<a href="data:file/csv;base64,{b64}" download="out.csv">Descargar Csv</a>', unsafe_allow_html=True)
