"""Pearson correlation."""

from math import sqrt


def pearson(pairs):
    """Return Pearson correlation for pairs.
    Using a set of pairwise ratings, produces a Pearson similarity rating.
    """

    series_1 = [float(pair[0]) for pair in pairs]   # unpacking zipped tuples into separate lists
    series_2 = [float(pair[1]) for pair in pairs]

    sum_1 = sum(series_1) # summing each list
    sum_2 = sum(series_2)

    squares_1 = sum([n * n for n in series_1]) # squaring each number; then adding sums (sum of squares)
    squares_2 = sum([n * n for n in series_2])

    product_sum = sum([n * m for n, m in pairs]) # for each pair, multiply scores by each other; then sum products

    size = len(pairs) #length of list of pairs

    # multiply sums of each list; divide by length of pair list; subtract from product_sum
    numerator = product_sum - ((sum_1 * sum_2) / size) 

    # for each individuals' scores list:
    # square the list sum and divide by length of pair list; subtract from sum of squares
    # multiply result for each person by other person; take the square root of product
    denominator = sqrt(
        (squares_1 - (sum_1 * sum_1) / size) *
        (squares_2 - (sum_2 * sum_2) / size)
    ) 

    if denominator == 0:
        return 0

    #do division
    return numerator / denominator
