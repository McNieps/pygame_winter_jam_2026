from game.entities.landmarks.landmark import *

landmark_dict: dict[str, type[Landmark]] = {
    "village": Village,
    "town": Town,
    "moor": Moor,
    "barrow": Barrow,
    "crossing": Crossing,
    "hallow": Hallow,
    "stubbing": Stubbing,
}
