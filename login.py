import time

import ddddocr
import requests
import base64

import utils

username = '15158132138'
password = '12345AaBb'
total_page = 1

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

for page in range(1, total_page + 1):
    courses = session.get(
        f"https://www.zjooc.cn/ajax?time={utils.generateRandomStringWithTimestamp(32)}&service=%2Fjxxt%2Fapi%2Fcourse%2FcourseStudent%2Fstudent%2Fcourse&params%5BpageNo%5D={page}&params%5BpageSize%5D=5&params%5BcoursePublished%5D=&params%5BcourseName%5D=&params%5BpublishStatus%5D=&params%5BbatchKey%5D=&checkTimeout=true",
        headers={"Referer": referer, "Signcheck": utils.calculateMd5(),
                 "Timedate": str(int(time.time() * 1000))}).json()

    for course in courses['data']:
        print(f'{course["id"]}: {course["name"]}')

        course_id = course["id"]

        print("=========")

        get_course_chapter_list = session.get(
            f"https://www.zjooc.cn/ajax?time={utils.generateRandomStringWithTimestamp(32)}&service=%2Fjxxt%2Fapi%2Fcourse%2FcourseStudent%2FgetStudentCourseChapters&params%5BpageNo%5D=1&params%5BcourseId%5D={course_id}&params%5BurlNeed%5D=0&checkTimeout=true",
            headers={"Referer": referer, "Signcheck": utils.calculateMd5(),
                     "Timedate": str(int(time.time() * 1000))}).json()

        for chapter in get_course_chapter_list['data']:
            chapter_id = chapter["id"]
            print(f'{chapter["id"]}: {chapter["name"]}')
            for child in chapter['children']:
                child_id = child['id']
                print(f'\t{child["id"]}: {child["name"]}')
                for sub_child in child['children']:
                    sub_child_id = sub_child['id']
                    print(f'\t\t{sub_child["id"]}: {sub_child["name"]}', end=' ')
                    get_video_progress = session.get(
                        f"https://www.zjooc.cn/ajax?time={utils.generateRandomStringWithTimestamp(32)}&service=%2Fjxxt%2Fapi%2Fcourse%2FcourseStudent%2FvideoProgress&params%5BchapterId%5D={sub_child_id}&params%5BcourseId%5D={course_id}&checkTimeout=true",
                        headers={"Signcheck": utils.calculateMd5(),
                                 "Timedate": str(int(time.time() * 1000))})
                    try:
                        play_progress = get_video_progress.json()['data']['percent']
                        print(f' {play_progress}%')
                        if play_progress != 100:
                            if (sub_child['originalResourceUrl'].endswith(".mp4")):
                                request_params = {
                                    'time': utils.generateRandomStringWithTimestamp(32),
                                    'service': '/learningmonitor/api/learning/monitor/videoPlaying',
                                    'params[courseId]': course_id,
                                    'params[chapterId]': sub_child_id,
                                    'params[playTime]': sub_child['vedioTimeLength'],
                                    'params[percent]': 100,
                                }

                            else:
                                request_params = {
                                    'time': utils.generateRandomStringWithTimestamp(32),
                                    'service': '/learningmonitor/api/learning/monitor/finishTextChapter',
                                    'params[courseId]': course_id,
                                    'params[chapterId]': sub_child_id,
                                    'checkTimeout': 'true'
                                }
                            print(session.get('https://www.zjooc.cn/ajax',
                                              params=request_params, headers={"Signcheck": utils.calculateMd5(),
                                                                              "Timedate": str(
                                                                                  int(time.time() * 1000))}).text)
                    except:
                        print(f"Error: {get_video_progress.text}\n")

            print()

        print("==================")

# /learningmonitor/api/learning/monitor/videoPlaying
# params%5BcourseId%5D: 8a2284e38a8df993018a91b347e0130a
# params%5BchapterId%5D: 8a2284e38a8df993018a91b35532139b
# params%5BplayTime%5D: 8a2284e38a8df993018a91b347e0130a
# params%5Bpercent%5D: 8a2284e38a8df993018a91b35532139b
