import os
import requests

message = ""
approve = True

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
headers = {'Authorization': f'token {GITHUB_TOKEN}'}
pr_number = os.environ['PR_NUMBER']
repo = 'https://github.com/Vincent-ice/5th-loongson-class-in-NEUQ'
review_url = f'{repo}/pulls/{pr_number}/reviews'
comment_url = f'{repo}/issues/{pr_number}/comments'
    

def check_branch():
    source_branch = os.environ['GITHUB_HEAD_REF']
    target_branch = os.environ['GITHUB_BASE_REF']
    if source_branch != 'homework1' or target_branch != 'homework1':
        message += 'PR 的源分支和目标分支必须都是 homework1。\n'
        approve = False

def check_sync():
    os.system('git fetch upstream')
    ahead_behind = os.popen('git rev-list --left-right --count HEAD...upstream/homework1').read().strip()
    ahead, behind = map(int, ahead_behind.split())
    if ahead > 0:
        message += '请将您的分支与上游同步。以下命令将您的分支与上游同步：'
        message += '`git pull upstream homework1`'
        approve = False
        
def check_changes():
    changed_files = os.popen('git diff --name-only HEAD HEAD~').read().strip().split('\n')
    if len(changed_files) != 1:
        message = '请仅在 ./作业提交 文件夹下创建一个符合 *的第一次提交.md 的文件。'
        approve = False

if __name__ == '__main__':
    check_branch()
    check_sync()
    check_changes()
    
    if approve:
        payload = {'event': 'APPROVE'}
        response = requests.post(review_url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception('无法添加 review。')
        else:
            print('已添加 review。')
    else:
        payload = {'body': f'@{os.environ["GITHUB_ACTOR"]} {message}'}
        response = requests.post(comment_url, headers=headers, json=payload)
        
        if response.status_code != 201:
            raise Exception('无法发布评论。\n' + message)
        else:
            print('已在 PR 评论区中发布评论。')