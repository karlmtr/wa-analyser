from glob import glob
import pathlib
import re
import os
from datetime import datetime
import matplotlib.pyplot as plt
import asyncio
import numpy as np

me = "Edward Galantay"
# me = "Lizzie"
typeLis = False

sp_events = [
    datetime(year = 2022,month=12, day = 24), # Noël 2022
    datetime(year = 2021,month=12, day = 24), # Noël 2021
    datetime(year = 2020,month=12, day = 24), # Noël 2020
    datetime(year = 2019,month=12, day = 24), # Noël 2019
]

def get_files(root_dir: str) -> list[pathlib.Path]:
    files = glob(os.path.join(root_dir, "*"))
    paths = [pathlib.Path(path) for path in files]
    return paths


async def read_file(path: pathlib.Path) -> tuple[str, str]:
    with open(path, "r") as fp:
        content = fp.read()
    otherName = path.name.split("with")[-1].lstrip().split(".")[-2]
    return otherName, content


# def get_numeric_infos(content: str, otherName: str) -> dict:
#     me_matches = re.findall(f"{me}:", content)
#     other_matches = re.findall(otherName + ":", content)
#     infos = {}

#     infos["nb_messages_me"] = len(me_matches)
#     infos["nb_messages_other"] = len(other_matches)
#     return infos


def get_datetimes(otherName, content: str) -> list[datetime]:
    if typeLis:
        date = (
            r"\[([0-9]{2}\.[0-9]{2}\.[0-9]{2},\s[0-9]{2}:[0-9]{2}:[0-9]{2}\s(?:AM|PM))\]\s("
            + f"{otherName}|{me})"
        )
        strptime_string = r"%d.%m.%y, %I:%M:%S %p"
    else:
        date = (
            r"([0-9]{2}\/[0-9]{2}\/[0-9]{4}, [0-9]{2}:[0-9]{2})\s-\s("
            + f"{me}|{otherName})"
        )
        strptime_string = r"%d/%m/%Y, %H:%M"

    # date = (
    #     r"\[([0-9]{2}\.[0-9]{2}\.[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2})\]\s("+f"{me}:"+f"|{otherName}:)"
    # )

    dates_matches = re.findall(date, content)
    # print(dates_matches)
    dates_me = []
    dates_other = []

    for match in dates_matches:
        date_obj = datetime.strptime(match[0], strptime_string)
        if match[1] == me:
            dates_me.append(date_obj)
        else:
            dates_other.append(date_obj)

    # if typeLis :
    #     dates: list[datetime] = [
    #         datetime.strptime(datetime_str, )
    #         for datetime_str in dates_matches
    #     ]
    # dates: list[datetime] = [
    #     datetime.strptime(datetime_str[0], "%d.%m.%y %H:%M:%S")
    #     for datetime_str in dates_matches
    # ]
    # else :

    #     dates: list[datetime] = [
    #         datetime.strptime(datetime_str[0], "%d/%m/%Y, %H:%M")
    #         for datetime_str in dates_matches
    #     ]
    # for i in range(len(dates)):
    #     if dates_matches[i][1] == me:
    #         dates_me.append(match[0])
    #     else :
    #         dates_other.append(match[0])

    return dates_me, dates_other


# def get_both_names(otherName, content):
#     name = f"({me}:\s|{otherName}:\s)"
#     matches = re.findall(name, content)
#     # print(matches)
#     return matches


def get_times(
    dt_me: list[datetime],
    dt_other: list[datetime],
) -> list[float]:
    """
    extract the dates to keep only hours and minutes for the messages in hours
    """
    hours_me = [date_me.time().hour + date_me.time().minute / 60 for date_me in dt_me]
    hours_other = [
        date_other.time().hour + date_other.time().minute / 60
        for date_other in dt_other
    ]
    return hours_me, hours_other


# def get_average_pause(otherName, content):
#     # get all dates
#     dates_me,dates_other = get_datetimes(otherName, content)
#     deltas = [(dates[i] - dates[i - 1]).seconds for i in range(1, len(dates))]
#     moy = np.mean(deltas) / 60  # moy en minutes

# return moy, deltas


async def main(file):
    otherName, content = await read_file(file)
    # names = get_both_names(otherName, content)
    dates_me, dates_other = get_datetimes(otherName, content)

    hours_me, hours_other = get_times(dates_me, dates_other)

    moy_hours = np.mean(hours_me + hours_other)

    # moy, deltas = get_average_pause(otherName, content)

    # times_me = []
    # times_other = []
    # print("fdsjkfslfklj", len(times), len(names))
    # for time, name in zip(times, names):
    #     if name == f"{me}: ":
    #         times_me.append(time)
    #     else:
    #         times_other.append(time)

    # dates_me = []
    # dates_other = []
    # for date, name in zip(dates, names):
    #     if name == f"{me}: ":
    #         dates_me.append(date)
    #     else:
    #         dates_other.append(date)

    # times_me = [date for date,name in zip(dates,names) if name == "Edward Galantay:"]
    # times_other = [date for date,name in zip(dates,names) if name == f"{otherName}:"]
    ### some extra infos
    # num_infos = get_numeric_infos(content=content, otherName=otherName)
    # print(
    #     f"""{5*"-"} {otherName} {5*"-"}\n{(num_infos["nb_messages_me"]/ (num_infos["nb_messages_me"] + num_infos["nb_messages_other"])* 100):.1f} % are my messages\nMoy heures jour : {moy_hours:.1f}\n"""
    # )
    ratio, = (
        len(dates_me) / len(dates_me + dates_other) *100
        if len(dates_me + dates_other) != 0
        else 0,
    )
    print(5 * "-", otherName, 5 * "-")
    print(f"Ratio: {ratio:.1f} %")
    print(f"Moy hour : {moy_hours:.1f}")
    print()
    
    
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(10, 10))
    fig.suptitle(f"{otherName}")
    ax1.set(
        title="Message distribution over date and time",
        ylabel="# messages",
        xlabel="dates",
    )
    for sp_event in sp_events : 
        ax1.axvline(x = sp_event, ls = "--", ymax=0.8)
    
    ax1.hist(
        dates_other,
        bins=100,
        label=f"{otherName} ({len(dates_other)} mess.)",
        alpha=0.5,
    )
    ax1.hist(dates_me, bins=100, label=f"{me} ({len(dates_me)} mess.)", alpha=0.5)
    ax1.legend()
    # ax1.hist(dates, bins=100)
    bins = 12 if typeLis else 24
    ax2.set(title="Message distribution in a day", xlabel="hour", ylabel="# messages")
    ax2.hist(hours_other, bins=bins, label=f"{otherName}", alpha=0.5)
    ax2.hist(hours_me, bins=bins, label=f"{me}", alpha=0.5)
    ax2.legend()
    # ax3.set(title="Distrib of time between 2 messages", xlabel="minutes", ylabel="# messages")
    # ax3.hist(deltas, bins=24)
    # fig.tight_layout()

    plt.savefig(os.path.join("results", otherName + ".png"))


if __name__ == "__main__":
    files = get_files("data")

    for file in files:
        asyncio.run(main(file))
