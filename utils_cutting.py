from typing import Tuple, List

from shapely.geometry import LineString


def calc_branch_index_cuted_by_line(coordinates_list, cut_line):
    for count, coordinates in enumerate(coordinates_list):
        if check_segments_are_crossing(cut_line, coordinates):
            return count
    return 0



def gets_start_end_to_cut(cutting_index: int, complete_l_string) -> Tuple[int, int]:
    """
    Loops trough string to find the indices of the corresponding end and start brackets between which the
    string should be cutted
    :param cutting_index: the index of the branch in the string which the cutting line intersected
    :return: start and end index of '[' and ']' bracket
    """
    next = "!"
    start_index = cutting_index
    while (next != "["):
        start_index = start_index - 1
        next = complete_l_string[start_index]

    end_index = cutting_index
    while (next != "]"):
        end_index += 1
        next = complete_l_string[end_index]
    return start_index, end_index


def check_segments_are_crossing(first_segment: List[Tuple[float, float]],
                                  second_segment: List[Tuple[float, float]]) -> bool:
    """
    Checks if the two segments given are crossing each other
    :param first_segment: start and end coordinates of first segment
    :param second_segment: start and end coordinates of second segment
    :return: true if they are crossing otherwise false
    """
    line_1 = LineString(first_segment)
    line_2 = LineString(second_segment)
    return line_1.intersects(line_2)