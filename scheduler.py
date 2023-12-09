import argparse
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import warnings
import pdb

def get_args_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('--addTask', action='store_true')
    parser.set_defaults(addTask=False)

    parser.add_argument('--removeTask', action='store_true')
    parser.set_defaults(removeTask=False)

    parser.add_argument('--viewTasks', action='store_true')
    parser.set_defaults(viewTasks=False)

    return parser

def get_user_response():
    question_list = [
        f"\nWhat is the name of the task you would like to add to your to-do list? ",
        f"(Optional) How long do you think this will this take you (in minutes)? ",
        f"(Optional) How important is this task to you on a scale of 1-100? ",
        f"(Optional) In how many days is this task due? ",
    ]

    task_name = None 
    task_length = None 
    task_importance = None 
    task_deadline = None
    question_id = 0

    while question_id < len(question_list):
        response = input(question_list[question_id])
        if question_id == 0:
            if response == "":
                print("Please enter a task name")
                continue
            else:
                task_name = response
        elif question_id == 1:
            if response != "":
                try:
                    task_length = int(response)
                    assert task_length > 0
                except:
                    print("Please enter a valid integer duration greater than 0 for your task, or leave it blank for the default 60 minutes.")
                    continue
            else:
                task_length = 60
        elif question_id == 2:
            if response != "":
                try:
                    task_importance = int(response)
                    assert task_importance >= 1
                    assert task_importance <= 100
                except:
                    print("Please enter a valid integer between 1-100 indicating the importance of your task, or leave it blank for the default 50 utils.")
                    continue
            else:
                task_importance = 50
        else:
            if response != "":
                try:
                    task_deadline = int(response)
                except:
                    print("Please enter an integer indicating days until your task is due, or leave it blank.")
                    continue
            else:
                task_deadline = None

        question_id += 1
    return task_name, task_length, task_importance, task_deadline

def remove_user_task(df):
    task_name = input("\nWhich task would you like to remove from your to-do list? ")

    # Select rows with the value "Alice" in the 'name' column
    mask = df['task_name'] == task_name

    if len(mask) > 0:
        # Drop the selected rows
        df.drop(df.index[mask], inplace=True)

        # save the new df
        df.to_csv('schedule.csv')

    return df
    

def load_or_create_dataframe():
    """
    This function tries to load a pandas data frame and if it doesn't exist it creates one.
    The data frame will have the columns "task_name", "task_length", "importance", "date_due"

    Returns:
    A pandas data frame.
    """

    try:
        # Try to load the data frame from a file
        df = pd.read_csv("schedule.csv", index_col=0)
    except FileNotFoundError:
        # If the file doesn't exist, create a new data frame
        df = pd.DataFrame(columns=["task_name", "task_length", "importance", "date_due"])
        # Save the data frame to a file
        df.to_csv("schedule.csv")

    return df

def get_due_date(days_from_now, df):
    """
    Gets the datetime of when the task is due for comparison
    """
    # Today's date
    today = datetime.today()

    if days_from_now is None:  # if deadline is unspecified
        df['date_due'] = pd.to_datetime(df['date_due'])
        latest_date = df['date_due'].max()
        if latest_date != np.nan:  # if the dataframe isn't empty, return the latest date + 1
            days_from_now = latest_date - today
            days_from_now = days_from_now.days + 1
        else:
            days_from_now = 1    

    # Date due
    date_due = today + timedelta(days=days_from_now)
    
    return date_due

def update_task_list(df, entry):
    """
    overwrites if it already exists or add to dataframe if it doesn't exist
    """
    task_name, task_length, task_importance, due_date = entry
    if entry['task_name'] in df['task_name'].values:  # if we've seen it
        task_name = entry['task_name']
        for key,value in entry.items():  # overwrite
            df.loc[df.task_name == task_name, key] = value
    else:
        df = df.append(entry, ignore_index=True)
    df.to_csv("schedule.csv")
    return df

def prioritize_tasks(df):
    task_utilities = set()

    df['date_due'] = pd.to_datetime(df['date_due'])

    today = datetime.today()
    for index, row in df.iterrows():
        delta_date_due = (row['date_due'] - today)
        delta_date_due = delta_date_due.days

        # importance should exponentially grow by due date
        task_utility = (np.exp(-delta_date_due) * row['importance']) / row['task_length'] 

        time_in_hours = round(row['task_length'] / 60, 2)  # used for printing

        task_utilities.add((row['task_name'], task_utility, time_in_hours))
    
    return sorted(task_utilities, key=lambda x: x[1], reverse=True)  # sort by utility from highest to lowest

def print_results(task_set, num_tasks=None):
    if num_tasks is None:
        num_tasks = min(len(task_set), 5)
        
    print(f"\nHere is the next set of tasks you should do in order:\n")
    for i in range(num_tasks):
        task_name, utility, time_in_hours = task_set[i]
        print(f"{i+1}. {task_name} - Estimated Time (in hours) = {time_in_hours}")
    print(f"\n")


def print_all_tasks(task_set):
    print_results(task_set, num_tasks=len(task_set))


def main(args):

    df = load_or_create_dataframe()
    
    if args.addTask:  # adding a task

        task_name, task_length, task_importance, task_deadline = get_user_response()

        due_date = get_due_date(task_deadline, df)

        new_entry = {"task_name": task_name, "task_length": task_length, "importance": task_importance, "date_due": due_date}
        
        df = update_task_list(df, new_entry)
    
    if args.removeTask:  # removing a task
        df = remove_user_task(df)
    
    if len(df) == 0:
        print("Schedule is clear! Add a task using the --addTask argument.")
        exit(0)

    sorted_tasks = prioritize_tasks(df)

    if args.viewTasks:
        print_all_tasks(sorted_tasks)
    else:
        print_results(sorted_tasks)


if __name__ == "__main__":
    parser = get_args_parser()
    args = parser.parse_args()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        main(args)