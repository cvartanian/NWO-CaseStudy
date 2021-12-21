import requests
import re
from sqlalchemy import create_engine
import pandas as pd
from sqlalchemy.sql.expression import false
from bs4 import BeautifulSoup




def get_genres():
    r = requests.get("https://www.imdb.com/feature/genre?ref_=fn_asr_ge")
    soup = BeautifulSoup(r.text,features="lxml")
    genres = soup.find_all("div",{"class":"full-table"})[0].text.split('      ')[1:-1]
        
    return genres

def get_movies(genre):
    print("Pulling " + genre)
    r = requests.get("https://www.imdb.com/search/title/?genres="+genre+"&explore=title_type,genres&view=simple")
    
    soup = BeautifulSoup(r.text,features="lxml")
    links = soup.find_all("a", href=re.compile("/title/tt"),text=re.compile("^((?!\n).)*$"))
    titles=[]
    for each in links:
        titles.append(each.text)

    return titles


if __name__ == "__main__":
    genres = get_genres()
    engine = create_engine('postgresql://chrisv:NWO@{}:5432/movies'.format('postgres_db'))
    # engine = create_engine('postgresql://chrisv:NWO@0.0.0.0:5432/movies')

    top=[]
    for genre in genres:
        movies = get_movies(genre.replace(" ",""))
        for index, movie in enumerate(movies):
            top.append({"genre":genre,"movie":movie,"rank":index})
    
    df = pd.DataFrame(top)
    df.to_sql('movie_ranking', engine,index=false,if_exists="append")
    print("Written to DB")

    print("Retrieving from DB")
    print(pd.read_sql_table('movie_ranking',con=engine))


    