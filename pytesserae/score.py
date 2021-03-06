"""Module for Tesserae scoring"""
import math


def vanilla(
    matching_terms,
    source_distance, target_distance,
    source_counts, target_counts,
):
    """Calculates the Tesserae score between from_source and from_target

        * matching_terms :: {str}
            A set of words found to match between the source and target
        * source_distance, target_distance :: int
            Distance between least frequent matching terms for source and
            target, respectively
        * source_counts, target_counts :: {str: int}
            A dictionary of word counts to consult in looking up frequency
            information

    Note that frequency for some word x in some text y refers to the number of
    times x appears in y divided by the total number of tokens in y.

    score = ln (
        (
            sum([1/f(t) for t in matching_terms]) +
            sum([1/f(s) for s in matching_terms])
        )
        / (d_t + d_s)
    )
        * f(t) is the frequency of a matching term in the target
        * f(s) is the frequency of a matching term in the source
        * d_t = target_distance
        * d_s = source_distance
    """
    target_size = sum([v for v in target_counts.values()])
    source_size = sum([v for v in source_counts.values()])
    return math.log(
        (
            sum([1 / (target_counts[t]/target_size) for t in matching_terms]) +
            sum([1 / (source_counts[s]/source_size) for s in matching_terms])
        ) / (target_distance + source_distance)
    )


def _get_two_lowest(matching_terms, counts):
    """Gets two lowest frequency matching terms

        * matching_terms :: {str}
            The set of matching words
        * counts :: {str: int}
            A dictionary of word counts for the text from which the chunk
            comes

    Assumes that len(matching_terms) >= 2
    """
    match_tuple = tuple(matching_terms)
    # tuple of (term, count)
    lowest = (match_tuple[0], counts[match_tuple[0]])
    next_lowest = (match_tuple[1], counts[match_tuple[1]])
    if lowest[1] > next_lowest[1]:
        tmp = lowest
        lowest = next_lowest
        next_lowest = tmp
    for term in match_tuple[2:]:
        term_count = counts[term]
        if term_count < lowest[1]:
            next_lowest = lowest
            lowest = (term, term_count)
        elif term_count < next_lowest[1]:
            next_lowest = (term, term_count)
    return lowest[0], next_lowest[0]


def _get_indices(term, chunk):
    """Get indices where term appears in chunk"""
    positions = []
    for i, token in enumerate(chunk):
        if token == term:
            positions.append(i)
    return positions


def find_distance(matching_terms, chunk, counts):
    """Calculates distance between matching terms in given chunk

        * matching_terms :: {str}
            The set of matching words
        * chunk :: [str]
            A chunk of text
        * counts :: {str: int}
            A dictionary of word counts for the text from which the chunk
            comes

    When there is only one matching term, the distance should be the smallest
    between instances of the matching term in chunk.

    Where there is more than one matching term, the distance should be the
    smallest between the instances of the lowest frequency matching term and
    the instances of the second lowest frequency matching term.
    """
    if len(matching_terms) == 1:
        # handle case where same term shows up multiple times in chunk
        term = tuple(matching_terms)[0]
        positions = _get_indices(term, chunk)
        # if this becomes a bottleneck, there is always numpy.diff
        inter_position_diffs = [
            j - i for i, j in zip(positions[:-1], positions[1:])]
        return min(inter_position_diffs)

    term1, term2 = _get_two_lowest(matching_terms, counts)
    term1_positions = _get_indices(term1, chunk)
    term2_positions = _get_indices(term2, chunk)
    # following lines might be improved with better algorithm
    min_dist = abs(term1_positions[0] - term2_positions[0])
    for pos1 in term1_positions:
        for pos2 in term2_positions:
            cur_dist = abs(pos2 - pos1)
            if cur_dist < min_dist:
                min_dist = cur_dist
    return min_dist
