#!/usr/bin/python3
def progressbar(current_value,total_value,bar_lengh,progress_char): 
    percentage = int((current_value/total_value)*100)                                                # Percent Completed Calculation 
    progress = int((bar_lengh * current_value ) / total_value)                                       # Progress Done Calculation 
    loadbar = "Progress: [{:{len}}]{}%".format(progress*progress_char,percentage,len = bar_lengh)    # Progress Bar String
    print(loadbar, end='\r')                                                                         # Progress Bar Output

if __name__ == "__main__":
    the_list = range(1,301) 
    for i in the_list:
        progressbar(i,len(the_list),30,'■')
    print("\n")