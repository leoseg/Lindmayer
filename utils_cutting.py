from typing import Tuple, List
import re
from shapely.geometry import LineString


def calc_branch_index_cuted_by_line(coordinates_list, cut_line):
    """
    Calulcates which branch was cutted and returns the index, if no
    index was cutted returns 0
    :param coordinates_list: coordinates of all branches
    :param cut_line: coordinates of cutting line
    :return: index
    """
    for count, coordinates in enumerate(coordinates_list):
        if check_segments_are_crossing(cut_line, coordinates):
            return count
    return 0


def check_if_tribe_cutted(string,cutting_index):
    """
    Checks if the tribe was cutted
    :param string: string of tree
    :param cutting_index: index where tree was cutted
    :return:
    """
    brackets_counter = 0
    for c in reversed(string[:cutting_index]):
         if c == "[": brackets_counter = brackets_counter +1
         if c == "]": brackets_counter = brackets_counter -1

    if (brackets_counter == 0):
        return True
    else:
        return False

def get_end_index(cutting_index: int, complete_l_string) -> int:
    """
    Gets index where cutted branch ends
    :param cutting_index: index of branch cutted in string
    :param complete_l_string: string of complete tree
    :return:
    """
    end_index = find_end_index_of_branch(complete_l_string[cutting_index],cutting_index,complete_l_string)
    return end_index

def find_end_index_of_branch(char,index,string):
    """
    Recursive functions thats finds the next ']' and retunrs index,
    if '[' is openend calls itself
    :param char: char at index
    :param index: index where to start
    :param string: string to loop trough
    :return: index of ']'
    """
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