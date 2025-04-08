import os
import sys
from git import Repo
from os import walk
import subprocess
import pycodestyle
import json
import re
#from loguru import logger
import logging
import shutil
import datetime

logging.basicConfig(filename = "checking_utils_functions.log",
                     format = '%(asctime)s%(message)s',
                     filemode='w')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


#Defining a get_logger function
def get_logger_instance(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  
    return logger


def git_hub_link_check(git_hub_link: str) -> str:
    match = re.search(r"github\.com/([a-zA-Z0-9_-]+)",git_hub_link)
    if not match:
        logger.error(f"Invalid GitHub URL format: {git_hub_link} through regular expression")
        return None
    try:
        if '/tree/' in git_hub_link:
            logger.info(f"Git hub link: {git_hub_link} contains tree")
            git_hub_link = git_hub_link.split('/tree/')[0]
        if not git_hub_link.endswith('.git'):
            logger.info(f"Git hub link: {git_hub_link} does not contain git")
            if git_hub_link.endswith("/"):
                logger.info(f"Git hub link: {git_hub_link} end with /")
                git_hub_link = git_hub_link[:-1]
                git_hub_link += '.git'
            else:
                git_hub_link += '.git'
        return git_hub_link
    except Exception as e:
        logger.info(f"Git hub link: {git_hub_link},this is the exception: {e} obtained")
        return None


#Function for cloning git in the working directory
def cloning_git(git_hub_link, repo_folder_naming_int_string):
    wor_dir = os.path.dirname(os.path.abspath(sys.argv[0])) 
    logger.info(f"this is the current working directory: {wor_dir} for this link: {git_hub_link}")
    repo_path = wor_dir + f"/repo_{repo_folder_naming_int_string}"
    logger.info(f"this is the repo_path: {repo_path}")
    try:
        Repo.clone_from(git_hub_link,repo_path)
        logger.info("the repository is getting cloned now")
        return repo_path
    except Exception as e:
        logger.error(f"this is the error obtained from git clone: {e}")
        return None


def remove_folders_and_subfolders(repo_path):
    removed = False
    for root, dirs, files in os.walk(repo_path):
        logger.info(f"The results from os.walk are root: {root}, dirs: {dirs}, files: {files}")
        for dir in dirs:
            if dir ==  "__pycache__" or dir == "venv":
                folder_path = os.path.join(root,dir)
                shutil.rmtree(folder_path)
                logger.info(f"the directory: {folder_path} has been deleted")
                continue

            folder_path = os.path.join(root,dir)
            logger.info(f"the current directory considered for removal is: {folder_path}")
            amount_of_directory = len(next(os.walk(folder_path))[1])
            logger.info(f"the amount of directory in the above folder path is: {amount_of_directory}")
            if amount_of_directory > 4:
                shutil.rmtree(folder_path)
                logger.info(f"the directory {folder_path} has been deleted")

        logger.info(f"The results from os.walk after deleting directory are: {root}, dirs: {dirs}, files: {files}")

    removed = True
    return removed, repo_path

def copy_files_to_main(repo_path):
    removed = False
    readme_names = ['README (2).md', 'readme-md.txt', 'README (1).md', 'readme (1).md', 'code README.md', 'README.md', 'readme.md', 'Readme.md', 'ReadMe.md', 'README', 'readme', 'umath-validation-set-README.txt', 'README.rst', 'readme.rst', 'README.txt', 'readme.txt']
    counter = 1
    for root, dirs, files in os.walk(repo_path, topdown=False):
        if root == repo_path:
            break
        logger.info(f"The results from os.walk are root: {root}, dirs: {dirs}, files: {files}")
        for file in files:
            hypothetical_final_file_path = repo_path + file

            if os.path.isfile(hypothetical_final_file_path):
                new_file_name_path = repo_path + f"{counter}" + file
                os.rename(hypothetical_final_file_path,new_file_name_path)
                counter += 1

            file_path = os.path.join(root,file)
            shutil.copy2(file_path,repo_path)
            os.remove(file_path)

        for dir in dirs:
            folder_path = os.path.join(root,dir)
            shutil.rmtree(folder_path)
            logger.info(f"the directory {folder_path} has been deleted")

    removed = True
    return removed, repo_path    


#Function for getting file_name
def getting_file_name(repo_path):
    f = []
    for (_, _, filenames) in walk(repo_path):
        f.extend(filenames)
        break
    return f


#Function for checking if read_me exists and contents of readme
def readme_check_if_exits(repo_path):
    f = getting_file_name(repo_path)
    logger.info(f"These are the files obtained: {f}")
    readme_check_variable = False
    read_me_file_name_list = []
    for item in f:
        if item[-3:] == ".md":
            read_me_file_name_list.append(item)
            logger.info(f"this is the name of the readme file: {read_me_file_name_list}")
            print("readme file exists")
            # if item[:-3].lower() == "readme":
            #     print("readme file exists")
            readme_check_variable = True
        else:
            readme_names = ['README (2).md', 'readme-md.txt', 'README (1).md', 'readme (1).md', 'code README.md', 'README.md', 'readme.md', 'Readme.md', 'ReadMe.md', 'README', 'readme', 'umath-validation-set-README.txt', 'README.rst', 'readme.rst', 'README.txt', 'readme.txt']
            if item in readme_names:
                read_me_file_name_list.append(item)
                logger.info(f"this is the name of the readme file: {read_me_file_name_list}")
                print("readme file exists")
                # if item[:-3].lower() == "readme":
                #     print("readme file exists")
                readme_check_variable = True

    
    return readme_check_variable,read_me_file_name_list,repo_path


#Function for checking the contents of readme
def readme_content_check(repo_path,read_me_file_name_list,word_count):
    readme_content_status = 0
    repo_name = repo_path.rpartition("/")[2]
    word_count_str = 0
    for read_me_file_name in read_me_file_name_list:
        mwc_file_path_string = f"./{repo_name}/{read_me_file_name}"
        logger.info(f"this is the path for markup check function: {mwc_file_path_string}")
        try:
            proc = subprocess.run(["mwc",mwc_file_path_string],
                            capture_output = True, text=True)
            logger.info(f"the result of markupcheck is here: {proc}")
            word_count_str += int(proc.stdout.partition("\n")[2].partition("\n")[0])
        except Exception as e:
            logger.info(f"this is the reason for markupcheck not working: {e}")
            word_count_str = -1
            readme_content_status = -1
            return readme_content_status,repo_path,word_count_str

    if word_count_str > word_count:
        readme_content_status = 1
    return readme_content_status,repo_path,word_count_str


def getting_py_file_paths(repo_path):
    #Extracting all .py files from the folder
    f = getting_file_name(repo_path)
    list_of_string = []

    for item in f:
        if item[-3:] == ".py":
            list_of_string.append(item)
    list_of_paths = []

    for py_files in list_of_string:
        list_of_paths.append(repo_path + f"/{py_files}")
        logger.info(f"These are the list of python file paths obtained: {list_of_paths}")
    return list_of_paths


#Function for checking no.of pep8 violations excluding warnings
def check_pycodestle_error(repo_path):
    list_of_pyfile_paths = getting_py_file_paths(repo_path)
    style = pycodestyle.StyleGuide(ignore = ['W191','W291','W292','W293',
                                             'W391','W605','W503','W504','W505','E501','E302','E305','E401'])
    result = style.check_files(list_of_pyfile_paths)
    logger.info(f"This is the result pycodestyle check: {result.get_statistics()}")
    logger.info(f"this is the count of total errors: {result.total_errors}")
    return result.total_errors


def check_ruff_error(repo_path):
    error_count = 0
    list_of_pyfile_paths = getting_py_file_paths(repo_path)
    for pyfile_path in list_of_pyfile_paths:
        proc = subprocess.run(["ruff","check",pyfile_path,"--output-format=json"],capture_output = True, text=True)
        logger.info(f"this is the result of ruff check: {proc}")
        try:
            errors = json.loads(proc.stdout)
            logger.info(f"this ruff_check errors are here: {errors}")
            if len(errors) == 0:
                logger.info("this file has passed ruff checks")
            else:
                logger.info(f"this is the number of ruff error instances: {len(errors)}")
                error_count += len(errors)
        except json.JSONDecodeError:
            return print("function failed")

    return error_count


def remove_folders_and_move_files_try(repo_path):
    removed = False
    
    # Traverse the directory tree bottom-up
    for root, dirs, files in os.walk(repo_path, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            new_path = os.path.join(repo_path, file)
            
            # Avoid overwriting existing files in the main directory
            if os.path.exists(new_path):
                base, ext = os.path.splitext(file)
                counter = 1
                while os.path.exists(new_path):
                    new_path = os.path.join(repo_path, f"{base}_{counter}{ext}")
                    counter += 1
            
            shutil.move(file_path, new_path)  # Move file to main directory
        
        # Remove subdirectories
        for dir in dirs:
            folder_path = os.path.join(root, dir)
            shutil.rmtree(folder_path)
    
    removed = True
    return removed, repo_path