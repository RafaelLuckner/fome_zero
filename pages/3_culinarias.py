# Imports
import inflection
import pandas as pd
import streamlit as st
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(page_title= 'Visão Cidades', layout='wide')

# Funçoes
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


def top_rest(num):
    """
    Essa função encontra um dos 5 restaurantes melhor avaliados das principais culinárias,
    para isso basta adicionar qual posição deseja, da posição 0 a 4 """
    cuisines = df1.loc[:,['cuisines','votes']].groupby('cuisines').sum().sort_values(by='votes',ascending=False).reset_index()
    cuisines = cuisines.iloc[0:5,:]
    cuisines = cuisines['cuisines'].unique()
    if len(cuisines)<5:
        return(1)
    else:
        if num == 100:
            return(0)
        else:
            cui = cuisines[num]
            colunas = ['aggregate_rating','cuisines','restaurant_name','restaurant_id']
            result = (df1.loc[df1['cuisines']==cui,colunas]
                                                         .groupby('restaurant_name')
                                                         .max()
                                                         .sort_values(by='aggregate_rating',ascending= False)
                                                         .reset_index())
            maxi = result.iloc[0,1]
            result = result.loc[result['aggregate_rating']== maxi,:].sort_values(by='restaurant_id',ascending=True)
            result = result.iloc[0:1,:]
            return(result)

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

df1 = df1.loc[df1['cuisines']!= 'nan',:]


st.markdown('# Visão Culinárias')
# Barra lateral 

image = Image.open('logo.png')
st.sidebar.image(image,width=200)

st.sidebar.markdown('# Zomato Restaurants')
st.sidebar.markdown('# ')
st.sidebar.markdown("""---""")

lista_variaveis = []
paises_selec = []
paises = df1['countries'].unique()

paises_var = st.sidebar.checkbox('Todos Países', value=True)
# Cria uma lista de variaveis com o nome dos paises
if paises_var == True: 
    paises_selec = paises
    
else: 
    for pais in paises:
        globals()[pais] = []
        variavel_pais = pais 
        lista_variaveis.append(variavel_pais)
    
    # Cria varias caixas com os nomes dos paises que devolvem bool
    # e são adicionadas numa lista se estiverem selecionadas
    st.sidebar.markdown('# Selecione os Países')
    for variavel, pais in zip(lista_variaveis, paises):
        variavel = st.sidebar.checkbox(pais,value=True)
        if variavel == True:
            paises_selec.append(pais)

st.sidebar.markdown("""---""")
num_res = st.sidebar.select_slider('Selecione a quantidade de Restaurantes que deseja visualizar na tabela',
                        options = range(1,21))
st.sidebar.markdown("""---""")

culinarias_var = st.sidebar.checkbox('Todas Culinarias', value=True)
if culinarias_var == True:
    culinaria_op = df1['cuisines'].unique()
else:
    culinarias = df1['cuisines'].unique()
    culinaria_op = st.sidebar.multiselect('Selecione as Culinárias (min 5)',culinarias)



#################### Filtros #############
df1 = df1.loc[df1['countries'].isin(paises_selec),:]
df1 = df1.loc[df1['cuisines'].isin(culinaria_op),:]
########################################



st.markdown('## Melhores Restaurantes dos Principais tipos de Culinária')

rest = top_rest(100)
if rest == 1:
    with st.container(border=True):
        st.markdown('### Selecione pelo menos 5 Culinárias!')
else:
    with st.container(border=True):
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            with st.container():
                rest=top_rest(0)
                texto = (f'{rest.iloc[0,2]} : {rest.iloc[0,0]}')
                st.markdown(f'###### <div style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{texto}</div>',
                            unsafe_allow_html=True)
                st.markdown(f'## {rest.iloc[0,1]}/5.0')
            
        with col2:
            with st.container():
                rest=top_rest(1)
                texto = (f'{rest.iloc[0,2]} : {rest.iloc[0,0]}')
                st.markdown(f'###### <div style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{texto}</div>',
                            unsafe_allow_html=True)
                st.markdown(f'## {rest.iloc[0,1]}/5.0')
                
        with col3:
            with st.container():
                rest=top_rest(2)
                texto = (f'{rest.iloc[0,2]} : {rest.iloc[0,0]}')
                st.markdown(f'###### <div style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{texto}</div>',
                            unsafe_allow_html=True)
                st.markdown(f'## {rest.iloc[0,1]}/5.0')
        with col4:
            with st.container():
                rest=top_rest(3)
                texto = (f'{rest.iloc[0,2]} : {rest.iloc[0,0]}')
                st.markdown(f'###### <div style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{texto}</div>',
                            unsafe_allow_html=True)
                st.markdown(f'## {rest.iloc[0,1]}/5.0')
                
        with col5:
            with st.container():
                rest=top_rest(4)
                texto = (f'{rest.iloc[0,2]} : {rest.iloc[0,0]}')
                st.markdown(f'###### <div style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{texto}</div>',
                            unsafe_allow_html=True)
                st.markdown(f'## {rest.iloc[0,1]}/5.0')


with st.container(border=True):
    st.markdown(f'### Top {num_res} Restaurantes por Avaliação')
    columns = ['restaurant_id','restaurant_name','city','countries',
               'cuisines','average_cost_for_two','aggregate_rating','votes']
    dfa = df1.loc[df1['aggregate_rating']== 4.9,columns].sort_values(by=['restaurant_id'],ascending=True)
    dfa = dfa.iloc[0:num_res].reset_index(drop=True)
    dfa





with st.container():
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown('### Top 10 Melhores Culinárias')
            dfa = (df1.loc[:,['cuisines','aggregate_rating']].groupby('cuisines')
                                                             .mean()
                                                             .reset_index()
                                                             .sort_values(by='aggregate_rating', ascending = False))
            dfa = dfa.iloc[0:10,:].reset_index(drop=True)
            dfa['aggregate_rating'] = dfa['aggregate_rating'].round(2)
            dfa.columns = ['Tipo de Culinária', 'Média de avaliação']
            st.plotly_chart(px.bar(dfa,x='Tipo de Culinária',y='Média de avaliação',text='Média de avaliação'))
            
    with col2:
        with st.container(border=True):
            st.markdown('### Top 10 Piores Culinárias')
            dfa = (df1.loc[:,['cuisines','aggregate_rating']].groupby('cuisines')
                                                             .mean()
                                                             .reset_index()
                                                             .sort_values(by='aggregate_rating', ascending = True))
            dfa = dfa.iloc[0:10,:].reset_index(drop=True)
            dfa['aggregate_rating'] = dfa['aggregate_rating'].round(2)
            dfa.columns = ['Tipo de Culinária', 'Média de avaliação']
            st.plotly_chart(px.bar(dfa,x='Tipo de Culinária',y='Média de avaliação',text='Média de avaliação'))













