import json
import time

import ddddocr
import requests
from requests import Session
import base64

import utils
from logger import get_logger
from constants import *

logger = get_logger(__name__)

with open('account.json') as f:
    account = json.load(f)
    username = account['username']
    password = account['password']
    total_page = account['totalPage']

# 开启会话
session: Session = requests.session()

ocr = ddddocr.DdddOcr()
captcha_data = session.get(url=LOGIN_PAGE_URL,
                           headers=HEADERS,
                           params=LOGIN_PAGE_PARAMETERS).json().get('data')

# 验证码id
captcha_id = captcha_data['id']
# 验证码识别结果
captcha_code = ocr.classification(base64.b64decode((captcha_data["image"])))

# 登陆信息表单
login_form = {
    'login_name': username,
    'password': password,
    'captchaCode': captcha_code,
    'captchaId': captcha_id,
    'redirect_url': REDIRECT_URL,
    'app_key': APP_KEY,
}

# 发送登陆POST请求
do_login = session.post(LOGIN_POST_URL, data=login_form)
if (do_login.json()['resultCode'] == 0):
    logger.info('用户登录成功')
else:
    logger.error('用户登录失败')
    exit()

# 获取授权码
authorization_code = do_login.json()['authorization_code']  # 这个授权码是不变的

session.get(
    f'https://www.zjooc.cn/login?time={utils.generateRandomStringWithTimestamp(32)}'
)

referer = f"https://www.zjooc.com/?auth_code={authorization_code}"

session.headers.update({'Referer': referer})

session.get(
    f'https://www.zjooc.cn/ajax?time={utils.generateRandomStringWithTimestamp(32)}&service=%2Fcms%2Fsystem%2Fmanage%2Fanniversary%2Fstate'
)
session.get(
    f"https://www.zjooc.cn/autoLogin?time={utils.generateRandomStringWithTimestamp(32)}&auth_code={authorization_code}&autoLoginTime=7&limitLoginTime="
)
user = session.get(
    f"https://www.zjooc.cn/ucenter/getUser?time={utils.generateRandomStringWithTimestamp(32)}",
    headers={'Referer': referer},
    verify=False)

for page in range(1, total_page + 1):
    courses = session.get(
        f"https://www.zjooc.cn/ajax?time={utils.generateRandomStringWithTimestamp(32)}&service=%2Fjxxt%2Fapi%2Fcourse%2FcourseStudent%2Fstudent%2Fcourse&params%5BpageNo%5D={page}&params%5BpageSize%5D=5&params%5BcoursePublished%5D=&params%5BcourseName%5D=&params%5BpublishStatus%5D=&params%5BbatchKey%5D=&checkTimeout=true",
        headers={
            "Referer": referer,
            "Signcheck": utils.calculateMd5(),
            "Timedate": str(int(time.time() * 1000))
        }).json()

    for course in courses['data']:
        logger.info(f'{course["id"]}: {course["name"]}')

        course_id = course["id"]

        get_course_chapter_list = session.get(
            f"https://www.zjooc.cn/ajax?time={utils.generateRandomStringWithTimestamp(32)}&service=%2Fjxxt%2Fapi%2Fcourse%2FcourseStudent%2FgetStudentCourseChapters&params%5BpageNo%5D=1&params%5BcourseId%5D={course_id}&params%5BurlNeed%5D=0&checkTimeout=true",
            headers={
                "Referer": referer,
                "Signcheck": utils.calculateMd5(),
                "Timedate": str(int(time.time() * 1000))
            }).json()

        for chapter in get_course_chapter_list['data']:
            chapter_id = chapter["id"]
            logger.info(f'{chapter_id}: {chapter["name"]}')
            for child in chapter['children']:
                child_id = child['id']
                logger.info(f'{child_id}: {child["name"]}')
                for sub_child in child['children']:
                    sub_child_id = sub_child['id']
                    logger.info(f'{sub_child_id}: {sub_child["name"]}')
                    get_video_progress = session.get(
                        f"https://www.zjooc.cn/ajax?time={utils.generateRandomStringWithTimestamp(32)}&service=%2Fjxxt%2Fapi%2Fcourse%2FcourseStudent%2FvideoProgress&params%5BchapterId%5D={sub_child_id}&params%5BcourseId%5D={course_id}&checkTimeout=true",
                        headers={
                            "Signcheck": utils.calculateMd5(),
                            "Timedate": str(int(time.time() * 1000))
                        })
                    try:
                        play_progress = get_video_progress.json(
                        )['data']['percent']
                        logger.info(f'progress {play_progress}%')
                        if play_progress != 100:
                            if (sub_child['originalResourceUrl'].endswith(
                                    ".mp4")):
                                request_params = {
                                    'time':
                                    utils.generateRandomStringWithTimestamp(
                                        32),
                                    'service':
                                    '/learningmonitor/api/learning/monitor/videoPlaying',
                                    'params[courseId]':
                                    course_id,
                                    'params[chapterId]':
                                    sub_child_id,
                                    'params[playTime]':
                                    sub_child['vedioTimeLength'],
                                    'params[percent]':
                                    100,
                                }

                            else:
                                request_params = {
                                    'time':
                                    utils.generateRandomStringWithTimestamp(
                                        32),
                                    'service':
                                    '/learningmonitor/api/learning/monitor/finishTextChapter',
                                    'params[courseId]':
                                    course_id,
                                    'params[chapterId]':
                                    sub_child_id,
                                    'checkTimeout':
                                    'true'
                                }

                            response = session.get(
                                'https://www.zjooc.cn/ajax',
                                params=request_params,
                                headers={
                                    "Signcheck": utils.calculateMd5(),
                                    "Timedate": str(int(time.time() * 1000))
                                }).text
                            logger.info(f'response: {response}')
                    except:
                        logger.error(f"Error: {get_video_progress.text}\n")

# /learningmonitor/api/learning/monitor/videoPlaying
# params%5BcourseId%5D: 8a2284e38a8df993018a91b347e0130a
# params%5BchapterId%5D: 8a2284e38a8df993018a91b35532139b
# params%5BplayTime%5D: 8a2284e38a8df993018a91b347e0130a
# params%5Bpercent%5D: 8a2284e38a8df993018a91b35532139b
