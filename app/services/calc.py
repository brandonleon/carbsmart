import math


def choose_servings(net_weight_grams: float, target_min_grams: float, target_max_grams: float) -> tuple[int, float]:
    if net_weight_grams <= 0:
        raise ValueError("Net weight must be positive")
    if target_min_grams <= 0 or target_max_grams <= 0:
        raise ValueError("Target range must be positive")
    if target_min_grams > target_max_grams:
        raise ValueError("Target min must be <= target max")

    max_servings = max(1, math.ceil(net_weight_grams / target_min_grams))
    midpoint = (target_min_grams + target_max_grams) / 2

    in_range: list[tuple[float, int, float]] = []
    out_range: list[tuple[float, float, int, float]] = []

    for servings in range(1, max_servings + 1):
        serving_weight = net_weight_grams / servings
        if target_min_grams <= serving_weight <= target_max_grams:
            in_range.append((abs(serving_weight - midpoint), servings, serving_weight))
        else:
            if serving_weight < target_min_grams:
                distance = target_min_grams - serving_weight
            else:
                distance = serving_weight - target_max_grams
            out_range.append((distance, abs(serving_weight - midpoint), servings, serving_weight))

    if in_range:
        _, servings, serving_weight = min(in_range)
        return servings, serving_weight

    _, _, servings, serving_weight = min(out_range)
    return servings, serving_weight


def calculate_plan(
    total_weight_grams: float,
    pan_weight_grams: float,
    total_carbs: float,
    target_min_grams: float,
    target_max_grams: float,
) -> tuple[float, int, float, float]:
    net_weight = total_weight_grams - pan_weight_grams
    if net_weight <= 0:
        raise ValueError("Total weight must be greater than pan weight")

    servings, serving_weight = choose_servings(net_weight, target_min_grams, target_max_grams)
    carbs_per_serving = total_carbs / servings if servings else 0.0
    return net_weight, servings, serving_weight, carbs_per_serving
