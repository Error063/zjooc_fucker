import json
import pprint
import sys
import time

import ddddocr
import requests
import base64

import utils

with open('account.json') as f:
    account = json.load(f)
    username = account['username']
    password = account['password']

total_page = 0


session = requests.session()
app_key = '1ddadc7d-6f0a-4eb0-b844-24dd28e33e74'

ocr = ddddocr.DdddOcr()
get_validate_code = session.get(
    f'https://centro.zjlll.net/ajax?time={time.time() * 1000}&service=%2Fcentro%2Fapi%2Fauthcode%2Fcreate&params=',
    verify=False)

img_base64 = get_validate_code.json()['data']['image']
validate_id = get_validate_code.json()['data']['id']

validate_code = ocr.classification(img=base64.b64decode(img_base64))

login_form = {
    'login_name': username,
    'password': password,
    'captchaCode': validate_code,
    'captchaId': validate_id,
    'redirect_url': 'https://www.zjooc.com',
    'app_key': app_key,
}

do_login = session.post('https://centro.zjlll.net/login/doLogin', data=login_form, verify=False)
print(do_login.text)
authorization_code = do_login.json()['authorization_code']

session.get(f'https://www.zjooc.cn/login?time={utils.generateRandomStringWithTimestamp(32)}')

referer = f"https://www.zjooc.com/?auth_code={authorization_code}"

session.headers.update({'Referer': referer})

session.get(
    f'https://www.zjooc.cn/ajax?time={utils.generateRandomStringWithTimestamp(32)}&service=%2Fcms%2Fsystem%2Fmanage%2Fanniversary%2Fstate')
session.get(
    f"https://www.zjooc.cn/autoLogin?time={utils.generateRandomStringWithTimestamp(32)}&auth_code={authorization_code}&autoLoginTime=7&limitLoginTime=")
user = session.get(f"https://www.zjooc.cn/ucenter/getUser?time={utils.generateRandomStringWithTimestamp(32)}",
                   headers={'Referer': referer}, verify=False)

print(user.text)
user_id = user.json()['data']['user']['id']

while True:
    course_list = session.get(
        "https://www.zjooc.cn/ajax",
        params={
            "time": utils.generateRandomStringWithTimestamp(32),
            "service": "/jxxt/api/course/courseStudent/student/course",
            "params[pageNo]": "1",
            "params[pageSize]": "5",
            "params[coursePublished]": "",
            "params[courseName]": "",
            "params[publishStatus]": "",
            "params[batchKey]": "",
            "checkTimeout": "true"
        },
        headers={
            "Referer": referer,
            "Signcheck": utils.calculateMd5(),
            "Timedate": str(int(time.time() * 1000))
        }
    )
    print(course_list.text)
    if course_list.json()['data']:
        for course in course_list.json()['data']:
            print(f'{course["id"]}: {course["name"]}')
            if time.time() >= utils.convertToUnixTimestamp(course['endDate']):
                print("Expired course! Stop", file=sys.stderr)
                break
            else:
                course_id = course['id']
                batchKey = course['batchId']
                for paper_type in range(1, 3):
                    print(f"Paper Type: {paper_type}")
                    page_count = 0
                    while True:
                        page_count += 1
                        query_test_papers = session.get(
                            "https://www.zjooc.cn/ajax",
                            params={
                                "time": utils.generateRandomStringWithTimestamp(32),
                                "service": "/tkksxt/api/admin/paper/student/page",
                                "params[pageNo]": f"{page_count}",
                                "params[pageSize]": "20",
                                "params[paperType]": f"{paper_type}",
                                "params[courseId]": course_id,
                                "params[keyword]": "",
                                "params[processStatus]": "",
                                "params[batchKey]": batchKey,
                                "checkTimeout": "true"
                            },
                            headers={
                                "Referer": referer,
                                "Signcheck": utils.calculateMd5(),
                                "Timedate": str(int(time.time() * 1000))
                            }
                        )
                        print(query_test_papers.json())
                        if query_test_papers.json()['data']:
                            for test_paper in query_test_papers.json()['data']:
                                print(f'{test_paper["paperId"]}: {test_paper["paperName"]}')
                                class_id = test_paper["classId"]
                                paper_id = test_paper["paperId"]

                                if paper_type == 1 and test_paper['allowCount'] <= test_paper['testCount']:
                                    print("Test over tries! Pass")
                                    continue

                                get_test_paper = session.get(
                                    "https://www.zjooc.cn/ajax",
                                    params={
                                        "time": utils.generateRandomStringWithTimestamp(32),
                                        "service": "/tkksxt/api/admin/paper/getPaperInfo",
                                        "params[paperId]": paper_id,
                                        "params[courseId]": course_id,
                                        "params[classId]": class_id,
                                        "params[batchKey]": batchKey,
                                        "checkTimeout": "true"
                                    },
                                    headers={
                                        "Referer": referer,
                                        "Signcheck": utils.calculateMd5(),
                                        "Timedate": str(int(time.time() * 1000))
                                    }
                                ).json()

                                if get_test_paper['data']:

                                    answer_form = {
                                        "service": "/tkksxt/api/student/score/sendSubmitAnswer",
                                        "body": "true",
                                        "params[batchKey]": batchKey,
                                        "params[id]": paper_id,
                                        "params[stuId]": user_id,
                                        # "params[clazzId]": get_test_paper['data']["classId"],
                                        "params[clazzId]": class_id,
                                        "params[scoreId]": get_test_paper['data']["scoreId"]
                                    }

                                    question_count = 0

                                    for question in get_test_paper['data']["paperSubjectList"]:
                                        question_id = question['id']
                                        answer = question['rightAnswer']
                                        subject_type = question['subjectType']
                                        answer_form[f"params[paperSubjectList][{question_count}][id]"] = question_id
                                        answer_form[
                                            f"params[paperSubjectList][{question_count}][subjectType]"] = subject_type
                                        answer_form[f"params[paperSubjectList][{question_count}][answer]"] = answer
                                        question_count += 1

                                    submit_paper = session.post(
                                        f"https://www.zjooc.cn/ajax",
                                        params={
                                            "time": utils.generateRandomStringWithTimestamp(32),
                                            "checkTimeout": "true"
                                        },
                                        data=answer_form,
                                        headers={
                                            "Referer": referer,
                                            "Signcheck": utils.calculateMd5(),
                                            "Timedate": str(int(time.time() * 1000))
                                        }
                                    )
                                    print("OK!" if submit_paper.json()['success'] else "ERR!")
                                else:
                                    print("Empty data!", file=sys.stderr)
                        if query_test_papers.json()['page']['end']:
                            print("No more tests! Stop", file=sys.stderr)
                            break


    if course_list.json()['page']['end']:
        print("No more course! Stop", file=sys.stderr)
        break
