import json
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
                print("Expired course! Stop")
                break
            else:
                course_id = course['id']
                batchKey = course['batchId']
                while True:
                    query_test_papers = session.get(
                        "https://www.zjooc.cn/ajax",
                        params={
                            "time": utils.generateRandomStringWithTimestamp(32),
                            "service": "/tkksxt/api/admin/paper/student/page",
                            "params[pageNo]": "1",
                            "params[pageSize]": "20",
                            "params[paperType]": "1",
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
                            if test_paper['allowCount'] <= test_paper['testCount']:
                                print("Test over tries! Pass")
                                continue
                    if query_test_papers.json()['page']['end']:
                        print("No more tests! Stop")
                        break


    if course_list.json()['page']['end']:
        print("No more course! Stop")
        break


for page in range(1, total_page + 1):
    courses = session.get(
        f"https://www.zjooc.cn/ajax?time={utils.generateRandomStringWithTimestamp(32)}&service=%2Fjxxt%2Fapi%2Fcourse%2FcourseStudent%2Fstudent%2Fcourse&params%5BpageNo%5D={page}&params%5BpageSize%5D=5&params%5BcoursePublished%5D=&params%5BcourseName%5D=&params%5BpublishStatus%5D=&params%5BbatchKey%5D=&checkTimeout=true",
        headers={"Referer": referer, "Signcheck": utils.calculateMd5(),
                 "Timedate": str(int(time.time() * 1000))}).json()

    for course in courses['data']:
        print(f'{course["id"]}: {course["name"]}')

        course_id = course["id"]

        print("=========")

        query_test_papers = session.get(
            "https://www.zjooc.cn/ajax",
            params={
                "time": utils.generateRandomStringWithTimestamp(32),
                "service": "/tkksxt/api/admin/paper/student/page",
                "params[pageNo]": "1",
                "params[pageSize]": "20",
                "params[paperType]": "1",
                "params[courseId]": course_id,
                "params[keyword]": "",
                "params[processStatus]": "",
                "params[batchKey]": "20240",
                "checkTimeout": "true"
            }
        )

        print("==================")