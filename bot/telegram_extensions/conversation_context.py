from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class ConversationContext:
    old_state: Optional[object]
    key: Tuple[int, ...]
