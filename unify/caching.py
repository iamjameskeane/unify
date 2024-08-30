import os
import json
from typing import Dict, Union
from openai.types.chat.chat_completion import ChatCompletion

_cache = None
_cache_fpath: str = os.path.join(os.getcwd(), ".cache.json")


def _create_cache_if_none():
    global _cache
    if _cache is None:
        if not os.path.exists(_cache_fpath):
            with open(_cache_fpath, "w") as outfile:
                json.dump({}, outfile)
        with open(_cache_fpath) as outfile:
            _cache = json.load(outfile)


# noinspection PyTypeChecker,PyUnboundLocalVariable
def get_cache(kw: Dict) -> Union[None, Dict]:
    _create_cache_if_none()
    kw = {k: v for k, v in kw.items() if v is not None}
    kw_str = json.dumps(kw)
    if kw_str in _cache:
        return ChatCompletion.parse_obj(json.loads(_cache[kw_str]))


# noinspection PyTypeChecker,PyUnresolvedReferences
def write_to_cache(kw, response):
    _create_cache_if_none()
    kw = {k: v for k, v in kw.items() if v is not None}
    kw_str = json.dumps(kw)
    response_str = json.dumps(response.model_dump())
    _cache[kw_str] = response_str
    with open(_cache_fpath, "w") as outfile:
        json.dump(_cache, outfile)