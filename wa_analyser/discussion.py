import pathlib
import re
from datetime import datetime
import pandas as pd


class Discussion:
    def __init__(self, path: pathlib.Path) -> None:
        with open(path, "r") as fp:
            self.content = fp.read()

    def to_dataframe(self) -> pd.DataFrame:
        reg_pat = r"\[?(\d{2}(?:\.|\/)\d{2}(?:\.|\/)\d{2,4},\s\d{2}:\d{2}(?:\:\d{2}\s(?:AM|PM))?)\]?\s(?:-\s)?((?:\w\s?)+):"
        matches = re.findall(reg_pat, self.content)
        dates = []
        names = []
        for date, name in matches:
            if len(name) < 40:
                try:
                    date_obj = datetime.strptime(date, r"%d/%m/%Y, %H:%M")
                except ValueError:
                    date_obj = datetime.strptime(date, r"%d.%m.%y, %I:%M:%S %p")
                dates.append(date_obj)
                names.append(name)
            else:
                print(name)

        df = pd.DataFrame({"date": dates, "name": names}).astype(
            {"date": "datetime64[ns]", "name": "category"}
        )
        return df
