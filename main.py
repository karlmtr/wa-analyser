from glob import glob
import pathlib
import os
import matplotlib.pyplot as plt
from wa_analyser import Discussion
import pandas as pd
import asyncio

import concurrent.futures


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
    users = df["name"].value_counts().index.to_list()
    nb_messages = {}
    
    for user in users:
        nb_messages[user] = df[df["name"] == user].count()
    
    infos["nb_messages"] = nb_messages # dict

    



def create_document(df):
    users = df["name"].value_counts().index.to_list()
    short_users = [user.split(" ")[0] for user in users]

    fig, (ax, ax1, ax2) = plt.subplots(nrows=3, ncols=1, figsize=(10, 7))
    fig.suptitle(f"{' & '.join(short_users)}")

    ax1.set(
        title="Message distrib. over time",
        ylabel="# messages",
        xlabel="dates",
    )
    ax2.set(
        title="Message distrib. over the day",
        ylabel="# messages",
        xlabel="dates",
    )
    for user in users:
        filt_df = df[df["name"] == user]
        ax1.hist(
            filt_df["date"],
            bins=100,
            label=f"{user} ({len(filt_df)}  mess. )",
            alpha=0.5,
        )
        ax2.hist(filt_df["date"].dt.hour, bins=24, alpha=0.5, label=user)
        ax1.legend()
        ax2.legend()

    fig.tight_layout()

    ## checking if the results folder already exists
    if not os.path.exists("./results/"):
        os.mkdir("./results")

    fig.savefig(f"./results/{'_'.join(short_users)}.pdf")


def main(file):
    disc = Discussion(file)
    df = disc.to_dataframe()
    create_document(df)


if __name__ == "__main__":
    files = get_files("data")
    # with concurrent.futures.ThreadPoolExecutor() as executor :
    #     results = [executor.submit(main(file)) for file in files]
    for file in files:
        main(file)
        break