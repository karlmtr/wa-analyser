from glob import glob
import pathlib
import os
import matplotlib.pyplot as plt
from wa_analyser import Discussion
import pandas as pd
import numpy as np
import datetime
import concurrent.futures


def get_files(root_dir: str) -> list[pathlib.Path]:
    files = glob(os.path.join(root_dir, "*"))
    paths = [pathlib.Path(path) for path in files]
    return paths


def who_creates_new_discussion(df):
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


def best_hour(df: pd.DataFrame):
    return (df["date"].dt.hour + df["date"].dt.minute / 60).mean()


# def get_reccurence_of_words(df: pd.DataFrame):
#     text_col = df["content"]
#     df["words"] = text_col.apply(tokenize_text)
#     exploded_df = df.explode("words")
#     word_counts = exploded_df["words"].value_counts()
#     print(word_counts)


def count_medias(df: pd.DataFrame):
    try:
        nb = df["content"].value_counts()["<Media omitted>\n"]
    except KeyError:
        return 0
    else:
        return nb


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
    infos["Moy. heures entre deux messages"] = round(
        np.mean(average_time_between_messages(df)), 1
    )
    return infos


def caracter_per_messages(df: pd.DataFrame):
    nb_caracters = df["content"].str.len().sum()
    nb_message = len(df["content"])
    return nb_caracters / nb_message


def average_time_between_messages(df: pd.DataFrame):
    diff = np.roll(df["date"], -1) - df["date"]
    return diff[:-1].dt.total_seconds() / 3600


def week_format(df: pd.DataFrame):
    return (
        df["date"].dt.day_of_week
        + df["date"].dt.hour / 24
        + df["date"].dt.minute / 1440
    )


def create_document(df: pd.DataFrame, specific_user=None):
    users = df["name"].value_counts().index.to_list()
    bigGroup = False
    if len(users) > 9 : 
       bigGroup = True 
    
    print(len(users))
    short_users = [user.split(" ")[0] for user in users]
    if not bigGroup : 
        fig, (ax, ax1, ax4, ax2, ax3) = plt.subplots(nrows=5, ncols=1, figsize=(30,40)) 
        fig.suptitle(f"{' & '.join(short_users)}")
    else : 
        fig, (ax, ax1, ax4, ax2, ax3) = plt.subplots(nrows=5, ncols=1, figsize=(30,40)) 
        

    ax1.set(
        title="Message distrib. / année",
        ylabel="# messages",
        xlabel="dates",
    )
    ax2.set(
        title="Message distrib. / jour",
        ylabel="# messages",
        xlabel="dates",
    )
    ax3.set(
        title="Nombre de 'relance' après X heures",
        ylabel="# relances",
        xlabel="Delta heure",
    )
    ax4.set(
        title="Messages dist. / semaine ",
        ylabel="# messages",
        xlabel="Jours semaine",
       
    )
    ax4.set_xticklabels(("","lundi", "mardi", "mercredi","jeudi","vendredi","samedi","dimanche"))

    ax.axis(False)
    MIN_Y, MAX_Y = ax.get_ylim()
    MIN_Y, MAX_Y = MIN_Y * 0.9, MAX_Y * 0.9  # padding
    MIN_X, MAX_X = ax.get_xlim()

    if not bigGroup :
        timedeltas, who_created = who_creates_new_discussion(df)
        for i, user in enumerate(users):
            filt_df = df[df["name"] == user]
            ax1.hist(
                filt_df["date"],
                bins=100,
                label=user,
                alpha=0.7,
            )
            ax2.hist(filt_df["date"].dt.hour, bins=24, alpha=0.7, label=user)

            ax3.plot(timedeltas, who_created[user], alpha=0.7, label=user)
            ax4.hist(week_format(filt_df), bins=24 * 7, alpha=0.7, label=user)

            ax.text(i / len(users), MAX_Y, user, va="center", ha="left", weight="bold")

            infos = get_infos(filt_df)
            for index, (key, value) in enumerate(infos.items()):
                ax.text(
                    i / len(users),
                    MAX_Y * 0.9 - index * 0.05,
                    f"{key} : {value}",
                    weight="light",
                )
    else : 
        ax1.hist(
            df["date"],
            bins=100,
            alpha=0.7,
        )
        ax2.hist(df["date"].dt.hour, bins=24, alpha=0.7)

        # ax3.plot(timedeltas, who_created[user], alpha=0.7)
        ax4.hist(week_format(df), bins=24 * 7, alpha=0.7)
        

    # ax4.hist2d(df[df["name
    ax.text(MIN_X, MAX_Y / 2, "General", weight="bold", va="center", ha="left")
    gen_infos = get_infos(df)
    for index, (key, value) in enumerate(gen_infos.items()):
        ax.text(
            MIN_X, MAX_Y / 2 * 0.8 - index * 0.05, f"{key} : {value}", weight="light"
        )

    if not bigGroup :
        ax1.legend()
        ax2.legend()
        ax3.legend()
        ax4.legend()
    
    fig.tight_layout()

    ## checking if the results folder already exists
    if not os.path.exists("./results/"):
        os.mkdir("./results")

    if not bigGroup:
        fig.savefig(f"./results/{'_'.join(short_users)}.pdf")
    else :
        fig.savefig(f"./results/group_{users[0]}.pdf")


def main(file):
    disc = Discussion(file)
    df = disc.to_dataframe()
    create_document(df)


if __name__ == "__main__":
    files = get_files("data")
    with concurrent.futures.ProcessPoolExecutor() as exec :
        results = [exec.submit(main, file) for file in files]
    # for file in files:
        # print(file)
    # main(pathlib.Path("data/test.txt"))
        # break
