from datetime import date, timedelta

import pytest

from beront.modules.commerce.domain.daily_selection import daily_choice


@pytest.mark.parametrize("count", [1, 2, 3, 4, 11, 32])
def test_daily_selection_is_stable_balanced_and_never_repeats_neighbors(count):
    identifiers = [str(i) for i in range(count)]
    start = date(2026, 11, 12)
    picks = [
        daily_choice(identifiers, start + timedelta(days=i), "home:welcome:niche")
        for i in range(count * 5)
    ]
    assert set(picks) == set(identifiers)
    if count > 1:
        assert all(a != b for a, b in zip(picks, picks[1:], strict=False))
    for i, chosen in enumerate(picks):
        assert chosen == daily_choice(
            list(reversed(identifiers)), start + timedelta(days=i), "home:welcome:niche"
        )
    ordinal = start.toordinal()
    for index in range(len(picks) - count):
        if (ordinal + index) % count == 0:
            assert len(set(picks[index : index + count])) == count


def test_no_candidates_and_duplicate_ids():
    day = date(2026, 11, 12)
    assert daily_choice([], day, "test") is None
    assert daily_choice(["a", "a"], day, "test") == "a"


def test_home_selection_reads_all_catalog_pages_and_keeps_private_configuration():
    from copy import deepcopy
    from datetime import UTC, datetime
    from types import SimpleNamespace
    from unittest.mock import MagicMock

    from beront.modules.commerce.application.featured_messages import FeaturedMessages

    rows = [{"slug": "welcome", "images": [{"url": "/old.webp"}], "image_ids": ["old"]}]
    products = [
        SimpleNamespace(
            id=str(index),
            name=f"Product {index}",
            brand_name="Fixture",
            classifications=["arabic" if index < 100 else "designer" if index == 100 else "niche"],
            images=[SimpleNamespace(position=0, asset_id=str(index), url=f"/media/{index}.webp")],
        )
        for index in range(102)
    ]
    uow = MagicMock()
    uow.__enter__.return_value = uow
    uow.commerce.messages.side_effect = lambda **_: deepcopy(rows)
    uow.catalog.candidates.side_effect = lambda _, offset, limit: products[offset : offset + limit]
    featured = FeaturedMessages(lambda: uow, now=lambda: datetime(2026, 11, 12, tzinfo=UTC))
    result = featured.listing()[0]
    assert len(result["images"]) == 3
    assert result["image_ids"][1:] == ["100", "101"]
    assert [call.kwargs["offset"] for call in uow.catalog.candidates.call_args_list] == [0, 100]
    uow.catalog.candidates.reset_mock()
    assert featured.listing(private=True) == rows
    uow.catalog.candidates.assert_not_called()
