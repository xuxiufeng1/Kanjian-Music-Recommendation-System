import numpy as np
import pandas as pd
from collections import defaultdict
from scipy.spatial.distance import cdist
from google.cloud import storage, bigquery
import joblib
import functions_framework
from flask import jsonify

PROJECT_ID = 'baidao-training-2023'
BUCKET_NAME = 'xu-2024'
MODEL_FILE = 'ml_model/model.joblib'

# 初始化 GCP 客户端
bq_client = bigquery.Client(project=PROJECT_ID)
storage_client = storage.Client(project=PROJECT_ID)
bucket = storage_client.bucket(BUCKET_NAME)

# 加载模型
model_blob = bucket.blob(MODEL_FILE)
model = joblib.load(model_blob.open("rb"))

# Spotify API 相关信息
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
client_id = '03b088703ba34455a239822051170123'
client_secret = '2506c50c0dec481e898ad564936f1372'
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
                                                           client_secret=client_secret))

number_cols = ['valence', 'year', 'acousticness', 'danceability', 'duration_ms', 'energy', 'explicit',
              'instrumentalness', 'key', 'liveness', 'loudness', 'mode', 'popularity', 'speechiness', 'tempo']

def find_song(name, year):
    """在 Spotify 上搜索歌曲，并返回包含歌曲特征的 DataFrame。"""
    song_data = defaultdict()
    results = sp.search(q= 'track: {} year: {}'.format(name,year), limit=1)
    if results['tracks']['items'] == []:
        return None

    results = results['tracks']['items'][0]
    track_id = results['id']
    audio_features = sp.audio_features(track_id)[0]

    song_data['name'] = [name]
    song_data['year'] = [year]
    song_data['explicit'] = [int(results['explicit'])]
    song_data['duration_ms'] = [results['duration_ms']]
    song_data['popularity'] = [results['popularity']]

    for key, value in audio_features.items():
        song_data[key] = value

    return pd.DataFrame(song_data)


def get_song_data(song, spotify_data):
    try:
        song_data = spotify_data[(spotify_data['name'] == song['name'])
                                & (spotify_data['year'] == song['year'])].iloc[0]
        return song_data
    
    except IndexError:
        return find_song(song['name'], song['year'])
        

def get_mean_vector(song_list, spotify_data):
    song_vectors = []
    for song in song_list:
        song_data = get_song_data(song, spotify_data)
        if song_data is None:
            print(f'Warning: {song["name"]} does not exist in Spotify or in database')
            continue
        song_vector = song_data[number_cols].values.flatten()
        song_vectors.append(song_vector)
    song_matrix = np.array(song_vectors)
    return np.mean(song_matrix, axis=0)

def flatten_dict_list(dict_list):
    """将字典列表转换为扁平化字典。"""
    flattened_dict = defaultdict()
    for key in dict_list[0].keys():
        flattened_dict[key] = []
    for dictionary in dict_list:
        for key, value in dictionary.items():
            flattened_dict[key].append(value)
    return flattened_dict

def recommend_songs(song_list, spotify_data, n_songs=10):
    """根据输入的歌曲列表推荐相似的歌曲."""

    metadata_cols = ['name', 'year', 'artists']
    song_dict = flatten_dict_list(song_list)
    song_center = get_mean_vector(song_list, spotify_data)
    song_center += np.random.normal(0, 0.1, size=song_center.shape)

    # 获取 StandardScaler 对象
    scaler = model.steps[0][1]

    # 使用 StandardScaler 缩放 song_center
    scaled_song_center = scaler.transform(song_center.reshape(1, -1)) 

    # 使用 StandardScaler 缩放 spotify_data
    scaled_data = scaler.transform(spotify_data[number_cols])

    distances = cdist(scaled_song_center, scaled_data, 'cosine')
    index = list(np.argsort(distances)[:, :n_songs][0])
    rec_songs = spotify_data.iloc[index]
    rec_songs = rec_songs[~rec_songs['name'].isin(song_dict['name'])]
    return rec_songs[metadata_cols].to_dict(orient='records')


@functions_framework.http
def recommend_songs_endpoint(request):
    """
    接收歌曲列表，并返回推荐歌曲列表的 Cloud Function 端点。
    """
    request_json = request.get_json(silent=True)

    # 使用更合适的名称来表示歌曲列表
    songs = request_json.get('songs', [])

    if not songs:
        return jsonify({'error': 'Missing "songs" key in request body'}), 400

    # 获取 Spotify 数据
    # spotify_data = pd.read_csv("gs://xuxf-training-2023/ml/data/data.csv")
    sql_query = f"""
        SELECT *
        FROM `baidao-training-2023.xu.ml_data`
    """
    spotify_data = bq_client.query(sql_query).to_dataframe()

    recommendations = recommend_songs(songs, spotify_data)
    return jsonify(recommendations)