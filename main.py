import os
import matplotlib.pyplot as plt
from wa_analyser import Discussion
import pandas as pd
import concurrent.futures
from wa_analyser.utils import *


def create_document(df: pd.DataFrame, specific_user=None):
    users = df["name"].value_counts().index.to_list()
    bigGroup = False
    if len(users) > 9:
        bigGroup = True

    short_users = [user.split(" ")[0] for user in users]
    if not bigGroup:
        fig, (ax, ax1, ax4, ax2, ax3) = plt.subplots(nrows=5, ncols=1, figsize=(15, 20))
        fig.suptitle(f"{' & '.join(short_users)}")
    else:
        fig, (ax, ax1, ax4, ax2, ax3) = plt.subplots(nrows=5, ncols=1, figsize=(30, 40))

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
    ax4.set_xticks([0, 1, 2, 3, 4, 5, 6])
    ax4.set_xticklabels(
        ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche")
    )

    ax.axis(False)
    MIN_Y, MAX_Y = ax.get_ylim()
    MIN_Y, MAX_Y = MIN_Y * 0.9, MAX_Y * 0.9  # padding
    MIN_X, MAX_X = ax.get_xlim()

    if not bigGroup:
        timedeltas, who_created = who_creates_new_discussion(df)
        average_time_response = average_time_between_response(df)
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
            infos[
                "Temps moyen de réponse"
            ] = f"{round(average_time_response[user],2)} h. ({int(average_time_response[user]*60)} min.)"
            for index, (key, value) in enumerate(infos.items()):
                ax.text(
                    i / len(users),
                    MAX_Y * 0.9 - index * 0.05,
                    f"{key} : {value}",
                    weight="light",
                )
    else:
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

    if not bigGroup:
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
    else:
        fig.savefig(f"./results/group_{users[0]}.pdf")


def main(file):
    print(file)
    disc = Discussion(file)
    df = disc.to_dataframe()
    create_document(df)


if __name__ == "__main__":
    files = get_files("data")
    with concurrent.futures.ProcessPoolExecutor() as exec:
        results = [exec.submit(main, file) for file in files]
