# Imports
import inflection
import pandas as pd
import streamlit as st
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(page_title= 'Visão Cidades', layout='wide')

# Funçoes para tratamento de dados
def country_name(country_id): 
    return COUNTRIES[country_id]

def rename_columns(dataframe):
    df1 = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df1.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df1.columns = cols_new
    return df1

def create_price_type(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"

def color_name(color_code):
    return COLORS[color_code]

# Dataset
df = pd.read_csv('zomato.csv')
df1=df

# Tratamento dos dados
# Renomeando todos os títulos das colunas para manter o mesmo padrão no nome
df1 = rename_columns(df1)

# Excluindo a coluna 'Switch to order menu' por ter o valor 0 em todas linhas 
df1 = df1.drop(columns =['switch_to_order_menu'])

# Excluindo todas linhas duplicadas da coluna 'Restaurant ID'
df1 = df1.drop_duplicates(subset=['restaurant_id']).reset_index(drop = True)

# Criando um dicionário referente a todos os países e seus codigos respectivos
COUNTRIES = {
1: "India",
14: "Australia",
30: "Brazil",
37: "Canada",
94: "Indonesia",
148: "New Zeland",
162: "Philippines",
166: "Qatar",
184: "Singapure",
189: "South Africa",
191: "Sri Lanka",
208: "Turkey",
214: "United Arab Emirates",
215: "England",
216: "United States of America",
}

# Criando uma nova coluna em df1 com o nome de cada país e excluindo a antiga
df1['countries'] = df1['country_code'].apply(lambda x: country_name(x))
df1 = df1.drop(columns = ['country_code'])

# Criando uma nova coluna com a categoria do restaurante e substituindo a antiga coluna 'price_range'
df1['category_food'] = df1['price_range'].apply(lambda x: create_price_type(x))
df1 = df1.drop(columns = ['price_range'])

# Criando um dicionário com o as cores referentes aos codigos e substituindo a coluna 'rating_color' pelos nomes das cores
COLORS = {
        "3F7E00": "darkgreen",
        "5BA829": "green",
        "9ACD32": "lightgreen",
        "CDD614": "orange",
        "FFBA00": "red",
        "CBCBC8": "darkred",
        "FF7800": "darkred"
}
    
# Criando uma nova coluna chamada colors e excluindo a antiga
df1['colors'] = df1['rating_color'].apply(lambda x: color_name(x))
df1 = df1.drop(columns = ['rating_color'])

# Mudando a coluna de cousines para string e pegando apenas o primeiro tipo de culinária 
df1["cuisines"] = df1.loc[:, "cuisines"].astype(str)
df1["cuisines"] = df1.loc[:, "cuisines"].apply(lambda x: x.split(",")[0])

st.markdown('# Visão Paises')
# Barra lateral 

image = Image.open('logo.png')
st.sidebar.image(image,width=200)

st.sidebar.markdown('# Zomato Restaurants')
st.sidebar.markdown('# ')
st.sidebar.markdown("""---""")

lista_variaveis = []
paises_selec = []
paises = df1['countries'].unique()

# Cria uma lista de variaveis com o nome dos paises
for pais in paises:
    globals()[pais] = []
    variavel_pais = pais 
    lista_variaveis.append(variavel_pais)

# Cria varias caixas com os nomes dos paises que devolvem bool e são adicionadas numa lista se estiverem selecionadas
st.sidebar.markdown('# Selecione os Países')
for variavel, pais in zip(lista_variaveis, paises):
    variavel = st.sidebar.checkbox(pais,value=True)
    if variavel == True:
        paises_selec.append(pais)



#################### Filtros #############
df1 = df1.loc[df1['countries'].isin(paises_selec),:]
########################################


with st.container(border=True):
    rest_cid = df1[['city','restaurant_id']].groupby('city').nunique().reset_index().sort_values(by='restaurant_id',ascending = False)   
    cid = rest_cid.iloc[0:10,:].reset_index(drop=True)
    cid.columns = ['Cidades', 'Restaurantes']
    st.plotly_chart(px.bar(cid, x='Cidades', y='Restaurantes', color= 'Cidades'))



with st.container():
    col1, col2 = st.columns(2)
    with col1:
        with st.container( border=True):
            st.markdown('##### Top 7 cidades com mais restaurantes com média de avaliação acima de 4')
            rest_cid = (df1.loc[df1['aggregate_rating']>=4,['countries','city','restaurant_id']].groupby(['countries','city'])
                                                                                                .count()
                                                                                                .reset_index()
                                                                                                .sort_values(by='restaurant_id',ascending = False)
                                                                                                .reset_index(drop=True))
            rest_cid.columns = ['Paises', 'Cidades', 'Restauranres']
            rest_cid = rest_cid.iloc[0:7,:].sort_values(by='Restauranres', ascending=False)
            
            st.plotly_chart(px.bar(rest_cid,x='Cidades',y='Restauranres',color='Paises'))
            
    with col2:
        with st.container( border=True):
            st.markdown('##### Top 7 cidades com mais restaurantes com média de avaliação abaixo de 2,5')
            rest_cid = (df1.loc[df1['aggregate_rating']<=2.5,['countries','city','restaurant_id']].groupby(['countries','city'])
                                                                                                .count()
                                                                                                .reset_index()
                                                                                                .sort_values(by='restaurant_id',ascending = False)
                                                                                                .reset_index(drop=True))
            rest_cid.columns = ['Paises', 'Cidades', 'Restauranres']
            rest_cid = rest_cid.iloc[0:7,:].sort_values(by='Restauranres', ascending=False)
            
            st.plotly_chart(px.bar(rest_cid,x='Cidades',y='Restauranres',color='Paises'))


with st.container(border=True):
    st.markdown('## Top 10 cidades com mais tipos culinários distintos')
    dis = (df1[['countries','city','cuisines']].groupby(['countries','city'])
                                               .nunique('cuisines')
                                               .reset_index()
                                               .sort_values(by='cuisines',ascending=False))
    dis.columns = ['País','Cidade','Culinária']
    dis = dis.iloc[0:10,:]
    st.plotly_chart(px.bar(dis,x='Cidade',y='Culinária',color='País'))























