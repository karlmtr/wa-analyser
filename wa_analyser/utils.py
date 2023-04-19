import pandas as pd
import numpy as np
import pathlib
import datetime
from glob import glob
import os
from textblob import Blobber
from textblob_fr import PatternTagger, PatternAnalyzer

tb = Blobber(pos_tagger=PatternTagger(), analyzer=PatternAnalyzer())


def week_format(df: pd.DataFrame):
    return (
        df["date"].dt.day_of_week
        + df["date"].dt.hour / 24
        + df["date"].dt.minute / 1440
    )


def average_time_between_response(df: pd.DataFrame) -> dict[str:float]:
    """General df, not user specific"""
    data = {}
    isNotSame = np.roll(df["name"], -1) != df["name"]
    diff = np.roll(df["date"], -1) - df["date"]
    df["diff"] = np.roll(diff.dt.total_seconds() / 3600, 1)
    corr_df = df[np.roll(isNotSame, 1)][1:]
    users = df["name"].unique()
    for user in users:
        data[user] = corr_df[corr_df["name"] == user]["diff"].mean()
    return data


def count_medias(df: pd.DataFrame):
    try:
        nb = df["content"].value_counts()["<Media omitted>\n"]
    except KeyError:
        return 0
    else:
        return nb


def best_hour(df: pd.DataFrame):
    return (df["date"].dt.hour + df["date"].dt.minute / 60).mean()


def who_creates_new_discussion(df):
    users = df["name"].unique()
    data = {user: [] for user in users}
    hours = np.arange(1, 50, 1)
    for hour in hours:
        diff = (np.roll(df["date"], -1) - df["date"]) > datetime.timedelta(
            days=0, hours=int(hour)
        )
        res = dict(df[np.roll(diff, 1)]["name"][1:].value_counts())
        for user in users:
            data[user].append(res[user])
    return hours, data


def old_who_creates_new_discussion(df):
    """
    df has to be general
    """
    users = df["name"].value_counts().index.to_list()
    data = {user: [] for user in users}
    time = np.arange(1, 50)
    for hour in time:
        delta = datetime.timedelta(days=0, hours=int(hour))
        temp_data = []
        for i in range(1, len(df["date"])):
            if df["date"][i] - df["date"][i - 1] > delta:
                temp_data.append(df["name"][i])
        for user in users:
            data[user].append(temp_data.count(user))
    return time, data


def get_files(root_dir: str) -> list[pathlib.Path]:
    files = glob(os.path.join(root_dir, "*"))
    paths = [pathlib.Path(path) for path in files]
    return paths


def get_infos(df: pd.DataFrame) -> dict:
    """
    Nb messages par user + pourcentage
    Meilleure heure dans la journée pour chaque user
    """
    infos = {}
    infos["Nb messages"] = len(df)
    infos["Meilleure heure (h)"] = round(best_hour(df), 1)
    infos["Caractère/message"] = round(caracter_per_messages(df), 1)
    infos["Nbre médias (audios compris)"] = count_medias(df)
    infos["Sentiment (entre -1 et +1)"] = round(get_sentiment_mean(df), 3)
    return infos


def caracter_per_messages(df: pd.DataFrame):
    nb_caracters = df["content"].str.len().sum()
    nb_message = len(df["content"])
    return nb_caracters / nb_message


def get_sentiment_mean(df: pd.DataFrame):
    get_sent = np.vectorize(apply_sentiment_alg)
    mean = np.mean(get_sent(df["content"]))
    return mean


def apply_sentiment_alg(message: str):
    blob = tb(message)
    return blob.sentiment[0]
