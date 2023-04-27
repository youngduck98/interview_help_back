from github import Github
import pytz, uuid, json, random
from flask import Blueprint, request, jsonify, make_response

# create a Github object, authenticated with an access token
g = Github("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")

# get a user by their GitHub username
user = g.get_user("youngduck98")

language_dict = {}
all_num = 1

for repo in user.get_repos():
    # Get the programming languages used in this repository
    repo_languages = repo.get_languages()
    # Append the programming languages to the list of languages used by the user
    for language in repo_languages:
        if  language not in language_dict:
            language_dict[language] = repo_languages[language]
        else:
            language_dict[language] += repo_languages[language]
        all_num += repo_languages[language]
lang_list = [[k,round(v/all_num * 100, 2)] for k, v in language_dict.items()]
lang_list.sort(key=lambda x:x[1], reverse=True)



# Print the list of programming languages used by the user
print("The user is proficient in the following programming languages:")
print(lang_list)