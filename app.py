from flask import Flask, render_template 
import pandas as pd
import requests
from bs4 import BeautifulSoup 
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')


app = Flask(__name__) #don't change this code

def scrap(url):
    #This is fuction for scrapping
    url_get = requests.get(url)
    soup = BeautifulSoup(url_get.content,"html.parser")
    
    #Find the key to get the information
    film = soup.find('div', attrs={'class':'lister-item mode-advanced'})

    #find movie title
    movie_title = []
    for title in soup.findAll('h3', {'class':'lister-item-header'}):
        titles = title.find('a', href = True).get_text()
        movie_title.append(titles)
    movie_title
    
    #genre
    genre_list = []
    for genre in soup.findAll('span', attrs= {'class':'genre'}):
        genre = genre.get_text()
        genre_list.append(genre.strip())
    genre_list
    
    #IMDB Rating
    imdb_rating = []
    for rating in soup.findAll('div', {'class':'ratings-bar'}):
        rating = rating.find('strong').get_text()
        imdb_rating.append(rating)
    imdb_rating
    
    #total votes
    total_votes = []
    movie_div = soup.find_all('div', class_='lister-item mode-advanced')

    for vote in movie_div:
        nv = vote.find_all('span', attrs={'name': 'nv'})
        vote = nv[0].text
        total_votes.append(vote)
    total_votes
    
    #metascores
    metascores = []

    for meta in movie_div:
        m_score = meta.find('span', class_='metascore').text if meta.find('span', class_='metascore') else '-'
        metascores.append(m_score)
    metascores
        
    import pandas as pd

    df = pd.DataFrame({
        'Movie': movie_title,
        'Genre': genre_list,
        'IMDB_Rating': imdb_rating,
        'Votes': total_votes,
        'Metascores' : metascores
        })
    df

   #data-wrangling
    df['IMDB_Rating'] = df['IMDB_Rating'].astype('float')
    
    def remove_str(votes):
        for r in ((',',''), ('(',''),(')','')):
            votes = votes.replace(*r)
        return votes
    
    df['Votes'] = df.Votes.apply(remove_str).astype(int)
    df['Votes'] = df['Votes'].astype('int64')

    return df

@app.route("/")
def index():
    df = scrap('https://www.imdb.com/search/title/?release_date=2019-01-01,2019-12-31')

    #This part for rendering matplotlib
    fig = plt.figure(figsize=(5,2),dpi=300)
    df.plot()
    
    #Do not change this part
    plt.savefig('plot1',bbox_inches="tight") 
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result = str(figdata_png)[2:-1]
    #This part for rendering matplotlib

    #this is for rendering the table
    df = df.to_html(classes=["table table-bordered table-striped table-dark table-condensed"])

    return render_template("index.html", table=df, result=result)


if __name__ == "__main__": 
    app.run()
