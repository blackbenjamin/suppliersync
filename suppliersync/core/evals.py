
def track_cost(tokens_in, tokens_out, price_per_1k_in=0.005, price_per_1k_out=0.015):
    return (tokens_in/1000.0)*price_per_1k_in + (tokens_out/1000.0)*price_per_1k_out
