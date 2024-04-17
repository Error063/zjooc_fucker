import base64
import time

import requests
import ddddocr

from constants import *
from . import utils, exceptions


class API:

    def __init__(self, account: str, password: str):
        """
        初始化登录类，完成登录流程

        参数:
        account: 账号，用于登录
        password: 密码，用于登录
        """
        # 创建会话
        self.session = requests.session()

        # 初始化OCR对象，用于识别验证码
        ocr = ddddocr.DdddOcr()
        # 获取验证码图片
        login_page_parameters: dict = {
            "time": time.time() * 1000,
            "service": "/centro/api/authcode/create",
            "params": ''
        }
        captcha_data = self.session.get(
            url=LOGIN_PAGE_URL, headers=HEADERS,
            params=login_page_parameters).json().get('data')
        # 从响应中提取验证码图片的base64编码和验证码ID
        # 验证码id
        captcha_id = captcha_data['id']
        # 验证码识别结果
        captcha_code = ocr.classification(
            base64.b64decode((captcha_data["image"])))

        # 构建登录表单数据
        login_form = {
            'login_name': account,
            'password': password,
            'captchaCode': captcha_code,
            'captchaId': captcha_id,
            'redirect_url': REDIRECT_URL,
            'app_key': APP_KEY,
        }

        # 发起登录请求
        do_login = self.session.post('https://centro.zjlll.net/login/doLogin',
                                     data=login_form,
                                     verify=False)
        # 登录失败处理
        if do_login.status_code != 200:
            raise exceptions.APIException(do_login.text)

        # 从登录响应中提取授权码
        authorization_code = do_login.json()['authorization_code']
        # 设置跳转链接，更新会话的Referer
        self.session.get(
            f'https://www.zjooc.cn/login?time={utils.generateRandomStringWithTimestamp(32)}'
        )
        self.referer = f"https://www.zjooc.com/?auth_code={authorization_code}"
        self.session.headers.update({'Referer': self.referer})

        # 完成登录流程的必要步骤
        self.session.get(
            f'https://www.zjooc.cn/ajax?time={utils.generateRandomStringWithTimestamp(32)}&service=%2Fcms%2Fsystem%2Fmanage%2Fanniversary%2Fstate'
        )
        self.session.get(
            f"https://www.zjooc.cn/autoLogin?time={utils.generateRandomStringWithTimestamp(32)}&auth_code={authorization_code}&autoLoginTime=7&limitLoginTime="
        )

        # 获取用户信息
        user = self.session.get(
            f"https://www.zjooc.cn/ucenter/getUser?time={utils.generateRandomStringWithTimestamp(32)}",
            headers={'Referer': self.referer},
            verify=False)

        # 用户信息获取失败处理
        if user.status_code != 200:
            raise exceptions.APIException(user.text)

        # 存储用户信息
        self.user = user.json()
        self.user_id = self.user['data']['user']['id']
        # 登录流程完成

    def get_user_course_list(self, page: int = 1) -> dict:
        """
        获取用户课程列表

        :param page: 请求的页码，默认为1
        :return: 返回课程列表的JSON数据
        """
        # 发起GET请求获取课程列表
        course = self.session.get(
            url="https://www.zjooc.cn/ajax",
            params={
                "service": "/jxxt/api/course/courseStudent/student/course",
                "params[pageNo]": page,
                "params[pageSize]": "5",
                "params[coursePublished]": "",
                "params[courseName]": "",
                "params[publishStatus]": "",
                "params[batchKey]": "",
                "checkTimeout": "true"
            },
            headers={
                "Referer": self.referer,
                "Signcheck": utils.calculateMd5(),  # 计算并设置签名
                "Timedate": str(int(time.time() * 1000))  # 设置请求时间戳
            })

        # 检查请求是否成功
        if course.status_code != 200:
            raise exceptions.APIException(course.text)  # 若请求失败，抛出API异常

        return course.json()  # 返回请求结果的JSON数据

    def get_course_chapter_list(self, course_id: str) -> dict:
        """
        获取指定课程的章节列表。

        参数:
        - course_id: str，课程的唯一标识符。

        返回值:
        - dict，包含章节信息的字典。

        异常:
        - 如果请求失败，将抛出APIException异常。
        """
        # 发起GET请求获取课程章节列表
        chapters = self.session.get(
            url="https://www.zjooc.cn/ajax",
            params={
                "time":
                utils.generateRandomStringWithTimestamp(32),  # 生成带有时间戳的随机字符串
                "service":
                "/jxxt/api/course/courseStudent/getStudentCourseChapters",
                "params[pageNo]": "1",  # 请求第一页数据
                "params[pageSize]": "5",  # 每页请求5条数据
                "params[courseId]": course_id,
                "params[urlNeed]": "",  # 需要的URL，此处为空
                "checkTimeout": "true"  # 检查超时
            },
            headers={
                "Referer": self.referer,  # 设置引用页面
                "Signcheck": utils.calculateMd5(),  # 计算MD5签名
                "Timedate": str(int(time.time() * 1000))  # 当前时间戳，毫秒级
            })
        # 如果请求返回的状态码不是200，则抛出异常
        if chapters.status_code != 200:
            raise exceptions.APIException(chapters.text)
        # 返回解析后的JSON数据
        return chapters.json()

    def get_user_video_progress(self, course_id: str, chapter_id: str) -> dict:
        """
        获取用户视频学习进度

        参数:
        course_id (str): 课程ID
        chapter_id (str): 章节ID

        返回:
        dict: 包含用户视频学习进度的字典
        """
        # 发起GET请求以获取用户指定课程和章节的视频学习进度
        learning_progress = self.session.get(
            url="https://www.zjooc.cn/ajax",
            params={
                "time":
                utils.generateRandomStringWithTimestamp(32),  # 生成带有时间戳的随机字符串
                "service":
                "/jxxt/api/course/courseStudent/videoProgress",  # 请求的服务接口
                "params[courseId]": course_id,  # 指定的课程ID
                "params[chapterId]": chapter_id,  # 指定的章节ID
                "checkTimeout": "true"  # 检查超时
            },
            headers={
                "Referer": self.referer,  # 设置引荐页信息
                "Signcheck": utils.calculateMd5(),  # 计算并设置MD5签名
                "Timedate": str(int(time.time() * 1000))  # 设置当前时间戳
            })
        # 如果请求返回的状态码不是200，则抛出API异常
        if learning_progress.status_code != 200:
            raise exceptions.APIException(learning_progress.text)
        # 返回请求得到的JSON数据
        return learning_progress.json()

    def send_course_finish_request(self, course_id: str, chapter_id: str,
                                   video_time: int) -> dict:
        """
        发送课程完成请求。

        参数:
        - course_id: 课程ID，字符串类型。
        - chapter_id: 章节ID，字符串类型。
        - video_time: 视频观看时间，整型。如果为-1，则表示完成文本章节。

        返回值:
        - 请求返回的JSON字典。

        抛出:
        - APIException: 如果请求返回的状态码不是200。
        """
        if video_time != -1:
            # 视频观看时间不为-1时，构建视频播放监控请求参数
            request_params = {
                'time': utils.generateRandomStringWithTimestamp(32),
                'service':
                '/learningmonitor/api/learning/monitor/videoPlaying',
                'params[courseId]': course_id,
                'params[chapterId]': chapter_id,
                'params[playTime]': video_time,
                'params[percent]': 100,
            }
        else:
            # 视频观看时间为-1时，构建文本章节完成监控请求参数
            request_params = {
                'time': utils.generateRandomStringWithTimestamp(32),
                'service':
                '/learningmonitor/api/learning/monitor/finishTextChapter',
                'params[courseId]': course_id,
                'params[chapterId]': chapter_id,
                'checkTimeout': 'true'
            }

        # 执行请求
        resp = self.session.get(url='https://www.zjooc.cn/ajax',
                                params=request_params,
                                headers={
                                    "Signcheck": utils.calculateMd5(),
                                    "Timedate": str(int(time.time() * 1000))
                                })

        # 请求异常处理
        if resp.status_code != 200:
            raise exceptions.APIException(resp.text)
        return resp.json()

    def get_test_papers(self, page: int, paper_type: int, course_id: str,
                        batch_key: str):
        """
        获取指定分区下的试卷列表。

        参数:
        page: int - 请求的页码
        paper_type: int - 试卷类型（例如：1代表测试分区，2代表作业分区）
        course_id: str - 课程的唯一标识符
        batch_key: str - 批次关键字，用于过滤试卷

        返回值:
        返回一个包含试卷信息的JSON对象。

        异常:
        如果请求失败，将抛出APIException异常。
        """

        # 发起GET请求获取试卷列表
        query_test_papers = self.session.get(
            "https://www.zjooc.cn/ajax",
            params={
                "time": utils.generateRandomStringWithTimestamp(
                    32),  # 生成随机字符串，作为请求的一部分
                "service": "/tkksxt/api/admin/paper/student/page",  # 请求的服务接口
                "params[pageNo]": page,  # 请求的页码
                "params[pageSize]": "20",  # 每页显示数量
                "params[paperType]": paper_type,  # 试卷分区类型
                "params[courseId]": course_id,  # 课程ID
                "params[keyword]": "",  # 关键字，用于搜索（此处为空）
                "params[processStatus]": "",  # 处理状态（此处为空）
                "params[batchKey]": batch_key,  # 批次关键字
                "checkTimeout": "true"  # 检查超时
            },
            headers={
                "Referer": self.referer,  # 请求的引用页面
                "Signcheck": utils.calculateMd5(),  # 计算的MD5签名
                "Timedate": str(int(time.time() * 1000))  # 当前时间戳，毫秒级
            })

        # 请求失败时，抛出异常
        if query_test_papers.status_code != 200:
            raise exceptions.APIException(query_test_papers.text)

        # 返回请求结果的JSON数据
        return query_test_papers.json()

    def submit_test_paper(self, paper_id: str, class_id: str, batch_key: str,
                          user_id: str, score_id: str, answers: list):
        """
        提交测试卷答案的函数。

        参数:
        - paper_id: 测试卷的ID。
        - class_id: 班级的ID。
        - batch_key: 批次关键字，用于标识一次提交。
        - user_id: 学生的ID。
        - score_id: 分数的ID，用于记录或识别学生的试卷。
        - answers: 从`get_test_papers()`获得的试卷。

        返回值:
        - 提交结果的JSON对象。

        抛出:
        - APIException: 如果提交答案时API响应的状态码不是200。
        """
        # 构建答案提交的表单数据
        answer_form = {
            "service": "/tkksxt/api/student/score/sendSubmitAnswer",
            "body": "true",
            "params[batchKey]": batch_key,
            "params[id]": paper_id,
            "params[stuId]": user_id,
            "params[clazzId]": class_id,
            "params[scoreId]": score_id
        }

        # 初始化题目计数器
        question_count = 0
        # 遍历答案列表，填充表单中关于题目和答案的信息
        for question in answers:
            question_id = question['id']
            answer = question['rightAnswer']
            subject_type = question['subjectType']
            answer_form[
                f"params[paperSubjectList][{question_count}][id]"] = question_id
            answer_form[
                f"params[paperSubjectList][{question_count}][subjectType]"] = subject_type
            answer_form[
                f"params[paperSubjectList][{question_count}][answer]"] = answer
            question_count += 1

        # 使用session发送表单数据，提交答案
        submit_paper = self.session.post(
            f"https://www.zjooc.cn/ajax",
            params={
                "time": utils.generateRandomStringWithTimestamp(32),
                "checkTimeout": "true"
            },
            data=answer_form,
            headers={
                "Referer": self.referer,
                "Signcheck": utils.calculateMd5(),
                "Timedate": str(int(time.time() * 1000))
            })

        # 如果提交状态码非200，抛出API异常
        if submit_paper.status_code != 200:
            raise exceptions.APIException(submit_paper.text)

        # 返回提交的JSON结果
        return submit_paper.json()


if __name__ == "__main__":
    account = ""
    password = ""
