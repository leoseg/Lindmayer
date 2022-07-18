from typing import Tuple, List
import re
from shapely.geometry import LineString


def calc_branch_index_cuted_by_line(coordinates_list, cut_line):

     for count, coordinates in enumerate(coordinates_list):
        if check_segments_are_crossing(cut_line, coordinates):
            return count
     return 0


def check_if_tribe_cutted(string,cutting_index):
     brackets_counter = 0
     for c in reversed(string[:cutting_index]):
         if c == "[": brackets_counter = brackets_counter +1
         if c == "]": brackets_counter = brackets_counter -1

     if (brackets_counter == 0):
        return True
     else:
        return False


def gets_start_end_to_cut(cutting_index: int, complete_l_string) -> Tuple[int, int]:
    """
    Loops trough string to find the indices of the corresponding end and start brackets between which the
    string should be cutted
    :param cutting_index: the index of the branch in the string which the cutting line intersected
    :return: start and end index of '[' and ']' bracket
    """
    next = "!"
    start_index = cutting_index

    while (next != "[" ):
        start_index = start_index - 1
        next = complete_l_string[start_index]
        if next == "]":
            while complete_l_string[start_index] not in ["F", "G", "R", "L"]:
                start_index +=1
            break



    end_index = cutting_index
    bracket_counter = 0
    next= "!"
    while (next != "]" or bracket_counter > 0):
        end_index += 1
        if next == "[" : bracket_counter += 1
        if next == "]" :
            bracket_counter -= 1
        next = complete_l_string[end_index]

    return start_index, end_index +1

def get_end_index(cutting_index: int, complete_l_string) -> int:
    end_index = find_end_index_of_branch(complete_l_string[cutting_index],cutting_index,complete_l_string)
    return end_index

def find_end_index_of_branch(char,index,string):
    next =char
    while (next != "]" ):
        index += 1
        next = string[index]
        if next == "[":
          index = find_end_index_of_branch(next,index,string)
    return index
def get_direction_of_cutted_branch(string:str, index):
    """
    Gets the direction of the branch, if a closed bracket appears before
    finding anything there is no direction just straightforward
    :param string: string to find direction
    :param index: start search from this index on backwards
    :return: string for direction
    """
    for char in reversed(string[:index]):
        if char == "]":
            return ""
        if char in ["+","-"]:
            return char

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