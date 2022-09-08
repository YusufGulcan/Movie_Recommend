import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer  # To vectorize the movie names
import re  # To clean text
from sklearn.metrics.pairwise import cosine_similarity  # To calculate similarity
from ipywidgets import widgets  # To create interactive interface
from IPython.display import display  # To create interactive interface
import streamlit as st
pd.set_option('display.width', 1000)

header = st.container()
dataset = st.container()
features = st.container()

with header:
    st.title('You Should Watch This!!!')
    st.text(
        'You Don\'t Know What To Watch ? \nI Can Help You.')

url = 'https://www.dropbox.com/s/slh5e7qzhqnjqqw/ratings.csv?dl=1'
url1 = 'https://www.dropbox.com/s/hjmdh3yrdck4gsd/movies.csv?dl=1'
@st.cache
movies_data = pd.read_csv(url1)
movies_data.head(3)

def clean_title(x):  # Create a function
    return re.sub('[^\w ]', '', x)  # This code removes anything except numbers,letters and blanks


movies_data['clean_title'] = movies_data.title.apply(
    lambda x: clean_title(x.strip()))  # Use the function to clean the title text in each row.

vec = TfidfVectorizer(ngram_range=(
1, 2))  # Vectorizer converts the test into numpy
# arrays, it takes single words and word pairs into consideration
vec_data = vec.fit_transform(movies_data.clean_title)  # Transform the cleaned text column


def search(query):
    query = clean_title(query)  # Clean the variable passed in the function
    query = vec.transform([query])  # Vectorize the variable   **  Only transform **
    similarity = cosine_similarity(query, vec_data).flatten()  # Calculate the  similarity score
    locs = np.append(np.argpartition(similarity, -10)[-10:],
                     np.argmax(similarity))  # Find 10 indices with the highest score
    movies = movies_data.iloc[locs][
             ::-1].drop_duplicates()  # Pass the indices in the movie data frame and create a new data frame.
    return movies

@st.cache
ratings = pd.read_csv(url)
ratings.head(3)


@st.cache
def recommendation(movie_id):
    # Get userIds of people who liked the movie registered with
    # the specified movie id. We can assume those users
    # are similar users. I will refer this group as similar users to make things clear.
    similar_users = ratings[(ratings.movieId == movie_id) & (ratings.rating > 4)]['userId'].unique()
    # Collect the Ids of the other movies that
    # similar people liked. Assume that similar people generally like similar movies.
    recs = ratings[(ratings.userId.isin(similar_users) == True) & (ratings.rating > 4)]['movieId']
    # Calculate which movie is liked how many times by similar
    # users and divide it to the total number of the group. It shows us the percentage of people who like the movie
    recs = recs.value_counts() / len(similar_users)
    # Filter the movies that are liked by at least %10 of the group.
    recs = recs[recs > 0.1]
    # The data that show all users who liked the movies that the at least % 10 of the similar users also liked.
    all_ = ratings[(ratings.movieId.isin(recs.index) == True) & (ratings.rating > 4)]
    # Calculate the ratio of the total population who liked the movies that the similar users liked.
    all_recs = all_['movieId'].value_counts() / len(all_['userId'].unique())
    # Concatenate the ratio tables to see the comparison
    combined_recs = pd.concat([recs, all_recs], axis=1)
    # Rename columns
    combined_recs.columns = ['similar', 'all']
    # To calculate the score we use the percentages.
    # If a movie is liked by similar people
    # but not popular among the total population, it is assumed to be a better recommendation,
    # because recommendation, in its nature,
    # is valuable when the asker do not know about the movie. So we take the raio between the score
    # among the similar people and the total population; the score is amplified when divided.
    combined_recs['score'] = combined_recs['similar'] / combined_recs['all']
    # Sort the data frame by score
    combined_recs = combined_recs.sort_values('score', ascending=False)
    # Merge scores and the movies data frames on movieId column, filter 3 columns and the first 10 rows.
    return combined_recs.merge(movies_data, left_index=True, right_on='movieId').head(10)[['title', 'genres', 'score']]


with features:
    title = st.text_input('You want to watch a similar movie to :', '')
    df1 = search(title)
    rec = recommendation(df1.iloc[0]['movieId'])
    st.dataframe(rec)  # Same as st.write(df)

#
# @st.cache
# def convert_df(df):
#     # IMPORTANT: Cache the conversion to prevent computation on every rerun
#     return df.to_csv().encode('utf-8')
#
#
# csv = convert_df(movies_data)
#
# st.download_button(
#     label="Download Movies as CSV",
#     data=csv,
#     file_name='movies_data.csv',
#     mime='text/csv',
# )
#
#
# csv1 = convert_df(movies_data)
#
# st.download_button(
#     label="Download Ratings as CSV",
#     data=csv1,
#     file_name='ratings_data.csv',
#     mime='text/csv',
# )