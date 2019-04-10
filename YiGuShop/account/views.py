from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, update_session_auth_hash
from django.core.mail import send_mail

# Create your views here.
def success_content(code=200,msg='ok',**datas):
    """ 返回成功信息 """
    content = {
        'status': {
            'code': code,
            'msg': msg
        }
    }
    if datas:
        data = {}
        for k, v in datas.items():
            data[k] = v
        content['data'] = data
        return content
    else:
        return content


def error_content(error_code, error_msg):
    """ 返回错误信息 """
    content = {
        "status": {
            "code": 400,
            "msg": {
                "error_code": error_code,
                "error_msg": error_msg
            }
        }
    }
    return content


def email_norm(email):
    """ 邮箱地址规范验证 """
    if len(email) > 7:
        import re
        re_str = '^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.' \
                 '([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$'
        if re.match(re_str, email) is not None:
            return 1
    return 0


class Register(View):
    """ 用户注册 """

    def get(self, request):
        """ 邮件验证页 """
        content = success_content(to_html='邮件验证页')
        return JsonResponse(content)

    def post(self, request):
        """ 获取密码，创建用户 """
        info = request.POST
        email = request.session.get('email', '')
        password = info.get('password', '')
        conpassword = info.get('conpassword', '')
        # 判断是否为空
        if email and password and conpassword:
            passwords = info['passwords']
            if email_norm(email) == 0:
                content = error_content(4003, '请输入有效邮箱！')
                return JsonResponse(content)
            elif len(password) > 15:
                content = error_content(4005, '密码过长')
                return JsonResponse(content)
            elif password != passwords:
                content = error_content(4009, '俩次密码不一致！')
                return JsonResponse(content)
            # 判断是否已存在
            try:
                User.objects.get(email=email)
                content = error_content(4001, '该用户名已注册！')
                return JsonResponse(content)
            except Exception as e:
                print(e)
                # 创建新用户
                user = User.objects.create_user(username=email,
                                                password=password, email=email)
                content = success_content(id=user.id, username=user.username)
                return JsonResponse(content)
        elif bool(email) is False:
            content = error_content(4003, '请先验证邮箱！')
            return JsonResponse(content)
        elif bool(password) is False or bool(conpassword) is False:
            content = error_content(4008, '密码不能为空！')
            return JsonResponse(content)
        content = error_content(4002, '不符合规范')
        return JsonResponse(content)


class Sendmail(View):
    """ 发送邮件验证码 """

    def get(self, request):
        """ 邮件验证页 """
        content = success_content(to_html='邮件验证页')
        return JsonResponse(content)

    def post(self, request):
        """ 发送邮件验证码 """

        info = request.POST
        email = info.get('email', '')
        # 保存会话
        request.session['emailaddress'] = email
        if email:
            if email_norm(email) == 0:
                content = error_content(4201, '请输入有效邮箱！')
                return JsonResponse(content)
            import random
            code = ''.join(random.sample(list('1234567890'), 5))
            print(code)
            try:
                send_mail('依谷网', '您的验证码为：%s' % code,
                          'wbovan@qq.com', [email], fail_silently=False)
                request.session['code'] = code
                print(code)
                content = success_content()
                return JsonResponse(content)
            except Exception as e:
                print('发送邮件错误：', e)
                content = error_content(4202, '邮箱发送失败，请重试！')
                return JsonResponse(content)
        content = error_content(4201, '请输入有效邮箱！')
        return JsonResponse(content)


class Verifycode(View):
    """ 判断验证码 """

    def post(self,request):
        code = request.session.get('code', None)
        getcode = request.POST.get('code', '')
        if code is None:
            content = error_content(4203, '请先发送验证码！')
            return JsonResponse(content)
        elif bool(getcode) is False:
            content = error_content(4204, '验证码不能为空！')
            return JsonResponse(content)
        if code == getcode:
            # 转移 保存会话
            email = request.session.get('emailaddress', '')
            request.session['email'] = email
            content = success_content()
            return JsonResponse(content)
        else:
            request.session['code'] = None
            content = error_content(4205, '验证码错误，请重新发送！')
            return JsonResponse(content)


class Resetpswd(View):
    """ 修改密码 """

    def get(self, request):
        """ 修改密码页 """
        content = success_content(to_html='修改密码页')
        return JsonResponse(content)

    def post(self, request):
        info = request.POST
        username = info.get('username', '')
        oldpassword = info.get('oldpassword', '')
        newpassword = info.get('newpassword', '')
        conpassword = info.get('conpassword', '')
        if username and oldpassword and newpassword and conpassword:
            try:
                User.objects.get(username=username)
            except Exception as e:
                print(e)
                content = error_content(4104, '用户名不存在！')
                return JsonResponse(content)
            user = authenticate(username=username,password=oldpassword)
            if user is None:
                content = error_content(4103, '密码错误！')
                return JsonResponse(content)
            if 5 > len(newpassword) > 15:
                content = error_content(4105, '密码格式错误！')
                return JsonResponse(content)
            if oldpassword == newpassword:
                content = error_content(4109, '新密码不能与最近密码相同！')
                return JsonResponse(content)
            if newpassword != conpassword:
                content = error_content(4106, '俩次密码不一致！')
                return JsonResponse(content)
            # 修改密码 并 保存
            user.set_password(newpassword)
            user.save()
            content = success_content(201,'Success')
            return JsonResponse(content)
        elif bool(username) is False:
            content = error_content(4107, '用户名不能为空！')
            return JsonResponse(content)
        elif bool(oldpassword) is False or bool(newpassword) is False or bool(conpassword) is False:
            content = error_content(4108, '密码不能为空！')
            return JsonResponse(content)



class Forgetpswd(View):
    """ 忘记密码 """

    def get(self, request):
        """ 邮件验证页 """
        content = success_content(to_html='邮件验证页')
        return JsonResponse(content)

    def post(self, request):
        """ 修改密码 """

        info = request.POST
        email = request.session.get('email', '')
        newpassword = info.get('newpassword', '')
        conpassword = info.get('conpassword', '')
        if email and newpassword and conpassword:
            try:
                user = User.objects.get(email=email)
            except Exception as e:
                print('忘记密码时报错：',e)
                content = error_content(4110, '邮箱不存在！')
                return JsonResponse(content)
            if 5 > len(newpassword) > 15:
                content = error_content(4113, '密码格式错误！')
                return JsonResponse(content)
            if newpassword != conpassword:
                content = error_content(4112, '俩次密码不一致！')
                return JsonResponse(content)
            user.set_password(newpassword)
            user.save()
            content = success_content(201,'Success')
            return JsonResponse(content)
        elif bool(email) is False:
            content = error_content(4114, '请先验证邮箱！')
            return JsonResponse(content)
        elif bool(newpassword) is False or bool(conpassword) is False:
            content = error_content(4115, '密码不能为空！')
            return JsonResponse(content)
        return JsonResponse('忘记密码post')
