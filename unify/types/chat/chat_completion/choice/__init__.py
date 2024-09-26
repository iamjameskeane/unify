from typing import Optional
from pydantic import ConfigDict
from openai.types.chat.chat_completion import Choice as _Choice

from ....base import _FormattedBaseModel
from .choice_logprobs import ChoiceLogprobs
from .chat_completion_message import ChatCompletionMessage


class Choice(_FormattedBaseModel, _Choice):
    model_config = ConfigDict(extra="forbid")
    # only override pydantic types  which require FormattedBaseModel
    logprobs: Optional[ChoiceLogprobs] = None
    message: ChatCompletionMessage
