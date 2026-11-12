def propose_patch(source):
    return source.replace(
        "return sum(prices_in_cents) + 1",
        "return sum(prices_in_cents)",
    )