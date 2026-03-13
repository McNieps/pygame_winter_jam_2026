from game.entities.landmarks.village import Village
from game.entities.landmarks.town import Town
from game.entities.landmarks.moor import Moor
from game.entities.landmarks.barrow import Barrow
from game.entities.landmarks.crossing import Crossing
from game.entities.landmarks.hallow import Hallow
from game.entities.landmarks.stubbing import Stubbing
from game.entities.landmarks.landmark import Landmark

landmark_dict: dict[str, type[Landmark]] = {
    "village": Village,
    "town": Town,
    "moor": Moor,
    "barrow": Barrow,
    "crossing": Crossing,
    "hallow": Hallow,
    "stubbing": Stubbing,
}
