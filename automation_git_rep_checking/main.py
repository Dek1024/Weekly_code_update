import utils
import pandas as pd

df_1 = pd.read_csv('test_data.csv')
df = pd.read_excel('175_Dayananda.xlsx',sheet_name="Sheet1")
print(df_1.columns)
df_1.drop(columns=['readme_if_exists',
       'readme_content', 'readme_word_count', 'ruff_error_count',
       'pycodestyle_error_count'],inplace=True)

df_1['git_hub_updated_link'] = None
df_1['readme_if_exists'] = None
df_1['readme_content'] = None
df_1['readme_word_count'] = None
df_1['sub_folder_removed'] = None
df_1['copied_files_to_main'] = None
df_1['ruff_error_count'] = None
df_1['pycodestyle_error_count'] = None
df_1['status'] = None
df_1['comments'] = None
repo_naming_variable = 1
word_count_threshold = 1 

logger = utils.get_logger_instance(__name__)

print(df_1.columns)
for index, row in df_1.iterrows():
    logger.info(f"the current index is : {index}")
    logger.info(f"the current candidate email id is: {row['Email Id']}")
    git_hub_link = row['GitHub repository link']
    git_hub_link = utils.git_hub_link_check(git_hub_link)
    print("Git_hub_link: ",git_hub_link)
    df_1.at[index,'git_hub_udpated_link'] = git_hub_link
    repo_path = utils.cloning_git(git_hub_link,repo_naming_variable)
    if repo_path == None:
        df_1.at[index,'comments'] = "there is an error in loading git_hub profile"
        repo_naming_variable += 1
        continue

    sub_folder_removed, repo_path = utils.remove_folders_and_subfolders(repo_path)
    if sub_folder_removed == True:
        df_1.at[index,'sub_folder_removed'] = sub_folder_removed

    files_copied, repo_path = utils.copy_files_to_main(repo_path)
    if files_copied  == True:
        df_1.at[index,'copied_files_to_main'] = sub_folder_removed

    check,read_file_name,repo_path = utils.readme_check_if_exits(repo_path)
    df_1.at[index,'readme_if_exists'] = check
    if check == False:
        df_1.at[index,'status'] = "Reject"
        df_1.at[index,'comments'] = "No readme file"
        repo_naming_variable += 1
        continue

    readme_content_status,repo_path,word_count = utils.readme_content_check(repo_path,read_file_name,word_count_threshold)
    df_1.at[index,'readme_content'] = readme_content_status
    df_1.at[index,'readme_word_count'] = word_count
    logger.info(f"the markdown workcounter gave this result: {word_count}")

    if readme_content_status == -1:
        df_1.at[index,'status'] = "Waitlist"
        df_1.at[index,'comments'] = "The word_counter is not working"
        repo_naming_variable += 1
        continue

    if readme_content_status == 0:
        df_1.at[index,'status'] = "Reject"
        df_1.at[index,'comments'] = "No content in readme file"
        repo_naming_variable += 1
        continue

    pycodesyle_error_count = utils.check_pycodestle_error(repo_path)
    df_1.at[index,'pycodestyle_error_count'] = pycodesyle_error_count
    ruff_error_count = utils.check_ruff_error(repo_path)
    df_1.at[index,'ruff_error_count'] = ruff_error_count
    df_1.to_csv('output.csv',mode='w+')
    # if repo_naming_variable == 20:
    #     break
    repo_naming_variable += 1

df.merge(df_1,how='inner',left_on='Email ID',right_on='Email Id')
df.to_excel("combined_ouput.xlsx",sheet_name='results')