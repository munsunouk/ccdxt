import datetime
import pathlib
import os
import re
from typing import Optional, Callable, Set, Union

def get_cached_item(self, fname: Union[str, pathlib.Path]) -> Optional[pathlib.Path]:

        path = self.get_cached_file_path(fname)
        if not os.path.exists(path):
            return None

        f = pathlib.Path(path)

        end_time_pattern = r"-to_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}"
        if re.search(end_time_pattern, str(fname)):
            # Candle files with an end time never expire, as the history does not change
            return f

        mtime = datetime.datetime.fromtimestamp(f.stat().st_mtime)
        if datetime.datetime.now() - mtime > self.cache_period:
            # File cache expired
            return None

        return f
    
