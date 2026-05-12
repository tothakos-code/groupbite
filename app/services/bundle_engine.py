import logging

from app.services.bundle_cache import BundleCache, get_bundle_cache

logger = logging.getLogger(__name__)


class BundleEngine:
    def __init__(self, cache: BundleCache):
        self._cache = cache

    def compute_matches(self, db, order_id: int, vendor_id) -> dict:
        from sqlalchemy.orm import joinedload
        from app.entities.user_basket import UserBasket
        from app.repositories.bundle_discount_repository import BundleDiscountRepository

        basket_rows = (
            db.query(UserBasket)
            .filter(UserBasket.order_id == order_id)
            .options(joinedload(UserBasket.item), joinedload(UserBasket.size))
            .all()
        )
        bundles = BundleDiscountRepository(db).find_by_vendor(vendor_id)

        raw_entries = [
            {
                "user_id": str(be.user_id),
                "menu_item_id": be.menu_item_id,
                "size_id": be.size_id,
                "count": be.count,
                "price": be.size.price,
                "category_id": be.item.category_id,
            }
            for be in basket_rows
        ]
        raw_bundles = [
            {
                "id": b.id,
                "name": b.name,
                "slots": [
                    {
                        "slot_index": s.slot_index,
                        "match_type": s.match_type,
                        "category_id": s.category_id,
                        "menu_item_id": s.menu_item_id,
                        "price_override": s.price_override,
                        "price_delta": s.price_delta,
                    }
                    for s in b.slots
                ],
            }
            for b in bundles
        ]

        return _run_matching(raw_entries, raw_bundles)

    def invalidate(self, order_id: int) -> None:
        self._cache.invalidate(order_id)


def _compute_delta(slot: dict, unit_price: int) -> int:
    if slot["price_override"] is not None:
        return slot["price_override"] - unit_price
    if slot["price_delta"] is not None:
        return -slot["price_delta"]  # price_delta is stored as a positive discount amount
    return 0


def _run_matching(basket_entries: list, bundles: list) -> dict:
    """
    Pure function — no DB access.

    basket_entries: [{user_id, menu_item_id, size_id, count, price, category_id}, ...]
    bundles:        [{id, name, slots: [{slot_index, match_type, category_id,
                      menu_item_id, price_override, price_delta}]}, ...]

    Returns: {(user_id, menu_item_id, size_id):
                {matched_units, applied_delta, bundle_name, bundle_id}}
    """
    result = {}

    # Expand basket entries into individual unit objects shared across all bundles.
    # Each unit carries a _matched flag so it can only be consumed once.
    remaining = []
    for entry in basket_entries:
        for _ in range(entry["count"]):
            remaining.append({
                "user_id": entry["user_id"],
                "menu_item_id": entry["menu_item_id"],
                "size_id": entry["size_id"],
                "price": entry["price"],
                "category_id": entry["category_id"],
                "_matched": False,
            })

    # Process bundles with the highest discount first so that a zero-discount or
    # misconfigured duplicate bundle cannot steal units away from the correct one.
    def _bundle_sort_key(b):
        max_delta = 0
        for s in b["slots"]:
            if s["price_delta"] is not None:
                max_delta = max(max_delta, s["price_delta"])
            elif s["price_override"] is not None:
                max_delta = max(max_delta, 1)  # price_override implies some discount
        return -max_delta  # most-discounted bundle sorts first

    bundles = sorted(bundles, key=_bundle_sort_key)

    for bundle in bundles:
        slots = sorted(bundle["slots"], key=lambda s: s["slot_index"])
        if len(slots) < 2:
            continue

        slot_map = {s["slot_index"]: s for s in slots}

        # Assign each unmatched unit to the first slot it qualifies for.
        slot_pools: dict = {s["slot_index"]: [] for s in slots}
        for unit in remaining:
            if unit["_matched"]:
                continue
            for slot in slots:
                if slot["match_type"] == "category" and slot["category_id"] == unit["category_id"]:
                    slot_pools[slot["slot_index"]].append(unit)
                    break
                if slot["match_type"] == "item" and slot["menu_item_id"] == unit["menu_item_id"]:
                    slot_pools[slot["slot_index"]].append(unit)
                    break

        if any(len(pool) == 0 for pool in slot_pools.values()):
            continue

        def _record(unit, slot_idx):
            unit["_matched"] = True
            key = (unit["user_id"], unit["menu_item_id"], unit["size_id"])
            delta = _compute_delta(slot_map[slot_idx], unit["price"])
            if key not in result:
                result[key] = {
                    "matched_units": 0,
                    "applied_delta": delta,
                    "bundle_name": bundle["name"],
                    "bundle_id": bundle["id"],
                }
            result[key]["matched_units"] += 1

        # Phase 1: same-user complete sets.
        all_users = set(u["user_id"] for pool in slot_pools.values() for u in pool)
        for user_id in all_users:
            per_slot = {si: [u for u in pool if u["user_id"] == user_id]
                        for si, pool in slot_pools.items()}
            n_sets = min(len(v) for v in per_slot.values())
            for si, user_units in per_slot.items():
                for u in user_units[:n_sets]:
                    slot_pools[si].remove(u)
                    _record(u, si)

        # Phase 2: cross-user sets with what remains.
        n_cross = min(len(pool) for pool in slot_pools.values())
        for si, pool in slot_pools.items():
            for u in pool[:n_cross]:
                _record(u, si)

    return result


bundle_engine = BundleEngine(get_bundle_cache())
