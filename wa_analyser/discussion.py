import pathlib
import re
from datetime import datetime
import pandas as pd

import glob


class Discussion:
    def __init__(self, path: pathlib.Path) -> None:
        with open(path, "r") as fp:
            self.content = fp.read()
            self.content = re.sub('', '', self.content )

    def to_dataframe(self) -> pd.DataFrame:
        # reg_pat = r"\[?(\d{2}(?:\.|\/)\d{2}(?:\.|\/)\d{2,4},\s\d{2}:\d{2}(?:\:\d{2}\s(?:AM|PM))?)\]?\s(?:-\s)?((?:\w\s?)+):\s"
        # reg_pat = r"\[?(\d{2}(?:\.|\/)\d{2}(?:\.|\/)\d{2,4},?\s\d{2}:\d{2}(?:\:\d{2}\s?(?:AM|PM)?)?)\]?\s(?:-\s)?((?:\w\s?)+):\s"
        reg_pat = r"\[?(\d{2}(?:\.|\/)\d{2}(?:\.|\/)\d{2,4},?\s\d{2}:\d{2}(?:\:\d{2}\s?(?:AM|PM)?)?)\]?\s(?:-\s)??((?:\+?\w\s?)+):\s"
        # matches = re.findall(reg_pat, self.content)
        dates = []
        names = []
        content = []
        oldEnd = 0
        first = True
        reg_matches = re.finditer(reg_pat, self.content) 
        message = ""
        match = None
        for match in reg_matches :    
            date = match[1]
            name = match[2]
            
            start, end = match.span()
            if len(name) < 40 :
                if not first:
                    message = self.content[oldEnd:start]
                    content.append(message) 
                try:
                    date_obj = datetime.strptime(date, r"%d/%m/%Y, %H:%M")
                except ValueError:
                    try :
                        date_obj = datetime.strptime(date, r"%d.%m.%y, %I:%M:%S %p")
                    except ValueError : 
                        try : 
                            date_obj = datetime.strptime(date, r"%d.%m.%y %H:%M:%S")
                        except ValueError :
                            date_obj = datetime.strptime(date, r"%d.%m.%y, %H:%M")
                dates.append(date_obj)
                names.append(name)
                
            oldEnd = end
            first = False  

        content.append(self.content[match.end():])
        df = pd.DataFrame({"date": dates, "name": names, "content" : content}).astype(
            {"date": "datetime64[ns]", "name": "category"}
        )
        return df

    