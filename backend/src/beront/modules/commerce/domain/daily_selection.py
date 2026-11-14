from datetime import date
from random import Random


def daily_choice(identifiers: list[str], day: date, namespace: str) -> str | None:
    ordered = sorted(set(identifiers))
    if not ordered:
        return None
    count = len(ordered)
    cycle, index = divmod(day.toordinal(), count)
    if count <= 2:
        Random(namespace).shuffle(ordered)
        return ordered[index]
    previous = ordered.copy()
    Random(f"{namespace}:{cycle - 1}").shuffle(previous)
    Random(f"{namespace}:{cycle}").shuffle(ordered)
    # Swapping the first two leaves each cycle's final item unchanged.
    if ordered[0] == previous[-1]:
        ordered[0], ordered[1] = ordered[1], ordered[0]
    return ordered[index]
