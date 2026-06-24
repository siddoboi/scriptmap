from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class LineType(Enum):
    SCENE_HEADING = "scene_heading"
    CHARACTER     = "character"
    PARENTHETICAL = "parenthetical"
    DIALOGUE      = "dialogue"
    ACTION        = "action"
    TRANSITION    = "transition"
    DUAL_DIALOGUE = "dual_dialogue"
    EMPTY         = "empty"


@dataclass
class DialogueLine:
    character:  str
    text:       str
    page:       int
    line_type:  LineType
    scene_id:   int
    sentiment:  Optional[float] = None
    is_dual:    bool = False


@dataclass
class SceneBlock:
    scene_id:            int
    heading:             str
    act:                 int
    page_start:          int
    page_end:            int
    characters_present:  list[str]
    dialogue:            list[DialogueLine] = field(default_factory=list)
    location:            Optional[str] = None
    time_of_day:         Optional[str] = None


@dataclass
class ScriptData:
    title:          str
    total_pages:    int
    scenes:         list[SceneBlock]
    characters:     dict[str, int]
    act_breaks:     list[int]
    source_format:  str
    parse_warnings: list[str] = field(default_factory=list)
    metadata:       dict      = field(default_factory=dict)