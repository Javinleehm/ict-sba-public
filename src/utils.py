import os
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import sys
plt.ion()

def set_current_directory_to_executable():
    """Set the current working directory to the directory of the executable."""
    if getattr(sys, 'frozen', False):
        # Running as an executable
        exe_path = os.path.dirname(sys.executable)
        os.chdir(exe_path)
    else:
        # Running as a script
        script_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_path)

set_current_directory_to_executable()

def validate_set_file(workspace,path):
    file_ext = os.path.splitext(path)[1]
    if file_ext == ".csv":
        ans_df = pd.read_csv(path)
        content = [ans_df[column].tolist() for column in ans_df]
        print(content[2])
        max_length = len(prev_read_ans(f"data/{workspace}/ans.csv")[1])
        for item in content[2]:
            if len(item) > max_length:
                return False
    else:
        return False
    return True
    
def prev_read_ans(path):
    file_ext = os.path.splitext(path)[1]
    if file_ext == ".csv":
        ans_df = pd.read_csv(path)
        # print(ans_df.head())
        return [ans_df[column].tolist() for column in ans_df]
    return []

def prev_workspace_can_ans_set(workspace_name,set_name):
    path = f"data/{workspace_name}/can_ans_set/{set_name}.csv"
    ans_df = pd.read_csv(path)
    return [ans_df[column].tolist() for column in ans_df]

def prev_workspace_can_ans_entry(workspace_name,entry_name):
    path = f"data/{workspace_name}/can_ans/{entry_name}.txt"
    f = open(path,"r")
    ans = ""
    for text in f.readlines():
        ans = ans+text[0]
    return ans

def list_can_ans_set(workspace_name):
    directory = f"data/{workspace_name}/can_ans_set"

    folders = []
    if os.path.exists(directory):
        for item in os.listdir(directory):
            # print(item)
            if not os.path.isdir(os.path.join(directory,item)):
                if os.path.splitext(item)[1] == ".csv":
                    folders.append(os.path.splitext(item)[0])
    return folders

def list_can_ans(workspace_name):
    directory = f"data/{workspace_name}/can_ans"
    folders = []
    if os.path.exists(directory):
        for item in os.listdir(directory):
            if not os.path.isdir(os.path.join(directory,item)):
                if os.path.splitext(item)[1] == ".txt":
                    folders.append(os.path.splitext(item)[0])
    return folders

def read_workspace_ans(workspace_name):
    path = "data/"+workspace_name+"/ans.csv"
    content = pd.read_csv(path)
    return [content[item].to_list() for item in content]

def list_workspaces():
    directory = "data"
    # Regular expression to match the pattern "temp-[uid]"
    pattern = re.compile(r'^temp-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    
    # List to store folder names
    filtered_folders = []
    while True:
        try:
            # Iterate over the items in the directory
            for item in os.listdir(directory):
                # Check if the item is a directory
                if os.path.isdir(os.path.join(directory, item)):
                    # Check if the folder name does not match the pattern
                    if not pattern.match(item):
                        filtered_folders.append(item)
            break
        except:
            os.mkdir("data")
    return filtered_folders

def evaluate_candidate_answers(workspace,ans_name,starting_score,correct_score,blank_deduction,wrong_deduction):
    ans_key,remarks = read_workspace_ans(workspace)
    can_ans_file = open(f"data/{workspace}/can_ans/{ans_name}.txt")
    can_ans = can_ans_file.readlines()
    for index in range(len(can_ans)):
        can_ans[index] = can_ans[index][0]
    result = []
    for index in range(len(can_ans)):
        if can_ans[index]==" ":
            result.append(" ")
        else:
            result.append(ans_key[index]==can_ans[index])
    return (result,score_calculator(result,starting_score,correct_score,blank_deduction,wrong_deduction))

def evaluate_dataset_answers(workspace,set_name,starting_score,correct_score,blank_deduction,wrong_deduction):
    ans_key,remarks = read_workspace_ans(workspace)
    can_id_set, can_name_set, can_ans_set = prev_workspace_can_ans_set(workspace,set_name)
    result_set = []
    index = 0
    for can_ans in can_ans_set:
        temp = []
        for i in range(len(can_ans)):
            if can_ans[i]==" ":
                temp.append(" ")
            else:
                temp.append(ans_key[i] == can_ans[i])
        result_set.append([can_id_set[index],can_name_set[index],temp,score_calculator(temp,starting_score,correct_score,blank_deduction,wrong_deduction),can_ans])
        index = index + 1
    std_scores = get_standard_score(result_set)
    for index in range(len(result_set)):
        result_set[index].append(std_scores[index])
    return result_set

def evaluate_dataset_answers(workspace,set_name,starting_score,correct_score,blank_deduction,wrong_deduction):
    ans_key,remarks = read_workspace_ans(workspace)
    print(f"The model answer key is {ans_key}")
    can_id_set, can_name_set, can_ans_set = prev_workspace_can_ans_set(workspace,set_name)
    print(f"The candidate id, name, and answers are: {(can_id_set, can_name_set, can_ans_set)}")
    result_set = []
    index = 0
    for can_ans in can_ans_set:
        temp = []
        for i in range(len(can_ans)):
            print(f"Evaluating question {i}")
            if can_ans[i]==" ":
                temp.append(" ")
                print("Blank answer")
            else:
                temp.append(ans_key[i] == can_ans[i])
                print(ans_key[i] == can_ans[i])
        result_set.append([can_id_set[index],can_name_set[index],temp,score_calculator(temp,starting_score,correct_score,blank_deduction,wrong_deduction),can_ans])
        print(f"Updated result:{result_set}")
        index = index + 1
    std_scores = get_standard_score(result_set)
    print(f"Standard score is {std_scores}")
    for index in range(len(result_set)):
        result_set[index].append(std_scores[index])
    return result_set

def evaluate_entry_answers(workspace,entry_name,starting_score,correct_score,blank_deduction,wrong_deduction):
    ans_key,remarks = read_workspace_ans(workspace)
    can_ans = prev_workspace_can_ans_entry(workspace,entry_name)
    result = []
    for i,ans in enumerate(can_ans):
        if ans == " ":
            result.append(" ")
        else:
            result.append(ans==ans_key[i])
    return result

def score_calculator(result,starting_score,correct_score,blank_deduction,wrong_deduction):
    score = starting_score
    for item in result:
        if item == " ":
            score = score - blank_deduction
        elif item == True:
            score = score + correct_score
        else:
            score = score - wrong_deduction
    return score

def get_max_attainable_score(workspace,starting_score,correct_score,blank_deduction,wrong_deduction):
    ans = prev_read_ans(f"data/{workspace}/ans.csv")
    return score_calculator([True]*len(ans[0]),starting_score,correct_score,blank_deduction,wrong_deduction)

def get_standard_score(result_set):
    scores = []
    for result in result_set:
        scores.append(result[3])
    
    mean_score = np.mean(scores)
    
    standard_deviation = np.std(scores,ddof=0)
    
    standard_scores = []
    
    for score in scores:
        if standard_deviation > 0:
            standard_scores.append(float((score - mean_score)/standard_deviation))
            # Avoids being numpy float instead of python float
        else:
            standard_scores.append(0)
    return standard_scores

# def get_mean_score(result_set):
#     sum = 0
#     for result in result_set:
#         sum = sum + result
#     return sum/len(result_set)

def get_standard_deviation(result_set):
    scores = []
    for result in result_set:
        scores.append(result[3])
    return np.std(scores,ddof=0)

def get_correct_percentage_graph(result_set):
    
    question_count = len(result_set[0][2])
    
    # Initialize zero arrays so multiple questions can be processed at once
    correct_counts = np.zeros(question_count)
    total_counts = np.zeros(question_count)
    
    # We only care whether candidates got questions correct
    for _,_,answers,_,_,_ in result_set:
        for i, answer in enumerate(answers):
            print(i,answer)
            if answer == True and answer != " ":
                correct_counts[i] += 1
            total_counts[i] += 1
    
    print(correct_counts)
    print(total_counts)
    percentages = (correct_counts/total_counts) * 100
    # Handles zero division case
    percentages = np.nan_to_num(percentages)
    
    # Generate graph
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(range(question_count), percentages, color='skyblue')
    ax.set_xticks(range(question_count))
    ax.set_xticklabels([f'Q{i+1}' for i in range(question_count)])
    ax.set_ylabel('Percentage of Correct Answers (%)')
    ax.set_title("Candidates' performance on individual question")
    ax.set_ylim(0, 100)  # Set y-axis limits from 0 to 100%
    ax.grid(axis='y')

    return fig  # Return the Figure object
    
def get_mean_score(result_set):
    score = 0
    for question_count,result in enumerate(result_set):
        score = score + result[3]
    return score/(question_count+1)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    result = evaluate_dataset_answers("AAAA","1C",0,1,0,0)
    print(result)
    graph = get_correct_percentage_graph(result)
    graph.show()
    input()