from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.models import User
from database.models import Receiving
from django.http import QueryDict


# Create your views here.

def verify_userid(userid, username):
    """
    检测传入用户id是否与当前用户name吻合，检测传入用户id是否存在
    :param userid: 请求连接带的用户id参数
    :param username: 当前已登录用户的name
    :return: 用户不存在返回False传入用户id与当前登录用户name不符合返回“verify”正确情况下返回user对象
    """
    if not userid:
        return False
    try:
        userid = int(userid)
    except ValueError:
        return False
    user_set = User.objects.filter(pk=userid)
    if not user_set:
        return False
    user = user_set[0]
    if user.username != username:
        return 'verify'
    return user


def verify_receiving(data):
    result_dict = {
        "status": {
            "code": 400,
            "msg": []
        }
    }
    if not data.get('name'):
        result_dict['status']['msg'].append({"error_code": 4420, "errpr_msg": "收货人名不可为空"})
    elif len(data['name']) > 10 or len(data['name']) < 2:
        result_dict['status']['msg'].append({"error_code": 4420, "errpr_msg": "收货人名过长/过短"})
    import re
    phone_pat = re.compile('^(13\d|14[5|7]|15\d|166|17[5|3|6|7]|18\d)\d{8}$')
    if not data.get('cell_phone'):
        result_dict['status']['msg'].append({"error_code": 4420, "errpr_msg": "请输入正确手机号"})
    elif not re.search(phone_pat, data.get('cell_phone')):
        result_dict['status']['msg'].append({"error_code": 4420, "errpr_msg": "请输入正确手机号"})
    if data.get('province') and data.get('city') and data.get('county') and data.get('specific_address'):
        pass
    else:
        result_dict['status']['msg'].append({"error_code": 4420, "errpr_msg": "地址不可为空"})
    if result_dict['status']['msg']:
        return (False,result_dict)
    return (True,data)


class Ubalance(View):
    """
    用户余额
    """

    def get(self, request):
        """
        查询当前用户的余额
        :param request: 请求对象
        :return: 无权限返回错误代码4303，用户不存在返回错误代码4303，查询成功返回查询结果
        """
        userid = request.GET.get('userid')
        username = request.session.get('username')
        user = verify_userid(userid, username)
        if not user:
            return JsonResponse({"status": {"code": 400, "msg": {"error_code": 4303, "error_msg": "用户不存在"}}},
                                status=400)
        if user != 'verify':
            balance = user.userprofile.balance
            return JsonResponse({"status": {"code": 200, "msg": "ok"}, "data": {"userid": user.id, "funds": balance}},
                                status=200)
        return JsonResponse({"status": {"code": 401, "msg": {"error_code": 4303, "error_msg": "没有查询权限"}}}, status=401)


class Udelivery(View):
    """
    收货地址
    """

    def get(self, request):
        """
        查询当前用户的所有收货地址
        :param request: 请求对象
        :return: 无权限返回错误代码4303，用户不存在返回错误代码4303，查询成功返回查询结果
        """
        userid = request.GET.get('userid')
        username = request.session.get('username')
        user = verify_userid(userid, username)
        if not user:
            return JsonResponse({"status": {"code": 400, "msg": {"error_code": 4303, "error_msg": "用户不存在"}}},
                                status=400)
        if user != 'verify':
            receiving_set = user.receiving_set.all()
            result = {"status": {"code": 200, "msg": "ok"},
                      "data": {"userid": userid,
                               "receiving_address": []
                               }
                      }
            for rece in receiving_set:
                receiving = {"id": rece.id,
                             "name": rece.name,
                             "telephone": rece.cell_phone,
                             "specific_address": rece.detailed,
                             "zip_code": rece.postal_code}
                result['data']['receiving_address'].append(receiving)
            return JsonResponse(result, status=200)
        return JsonResponse({"status": {"code": 401, "msg": {"error_code": 4303, "error_msg": "没有查询权限"}}}, status=401)

    def post(self, request):
        data = request.POST
        userid = data.get('userid')
        username = request.session.get('username')
        user = verify_userid(userid, username)
        if not user:
            return JsonResponse({"status": {"code": 400, "msg": {"error_code": 4303, "error_msg": "用户不存在"}}},
                                status=400)
        if user == 'verify':
            return JsonResponse({"status": {"code": 401, "msg": {"error_code": 4303, "error_msg": "没有访问权限"}}},
                                status=401)
        data = verify_receiving(data)
        if not data[0]:
            return JsonResponse(data[1],status=400)
        data = data[1]
        user_obj = User.objects.get(pk=userid)
        rece_obj = Receiving(name=data['name'],cell_phone=data['cell_phone'],province=data['province'],
                             city=data['city'],district=data['district'],detailed=data['detailed'],user=user_obj)
        if data.get('postal_code'):
            rece_obj.postal_code = data['postal_code']
        if data.get('phone'):
            rece_obj.phone = data['phone']
        if data.get('is_default'):
            rece_obj.is_default = True
        rece_obj.save()
        return JsonResponse({"status":{"code":201,"msg":"添加成功！"}},status=200)

    def put(self,request):
        data = QueryDict(request.body)
        userid = data.get('userid')
        username = request.session.get('username')
        user = verify_userid(userid, username)
        if not user:
            return JsonResponse({"status": {"code": 400, "msg": {"error_code": 4303, "error_msg": "用户不存在"}}},
                                status=400)
        if user == 'verify':
            return JsonResponse({"status": {"code": 401, "msg": {"error_code": 4303, "error_msg": "没有访问权限"}}},
                                status=401)
        try:
            rece_id = int(data.get('receiving_id'))
        except ValueError:
            return JsonResponse({"status": {"code": 400, "msg": {"error_code": 44422, "error_msg": "收货地址不存在"}}},
                                status=400)
        if rece_id not in [item.id for item in user.receiving_set.all()]:
            return JsonResponse({"status": {"code": 401, "msg": {"error_code": 4303, "error_msg": "没有访问权限"}}},
                                status=401)
        rece_obj = Receiving.objects.get(pk=rece_id)
        result_dict = {
            "status": {
                "code": 400,
                "msg": []
            }
        }
        if not data.get('name'):
            result_dict['status']['msg'].append({"error_code": 4420, "errpr_msg": "收货人名不可为空"})
        elif len(data['name']) > 10 or len(data['name']) < 2:
            result_dict['status']['msg'].append({"error_code": 4420, "errpr_msg": "收货人名过长/过短"})
        else:
            rece_obj.name = data.get('name')
            result_dict['status']['msg'].append({"name": "收货名成功修改！"})
        import re
        phone_pat = re.compile('^(13\d|14[5|7]|15\d|166|17[5|3|6|7]|18\d)\d{8}$')
        if not data.get('cell_phone'):
            result_dict['status']['msg'].append({"error_code": 4420, "errpr_msg": "手机号不可为空"})
        elif not re.search(phone_pat, data.get('cell_phone')):
            result_dict['status']['msg'].append({"error_code": 4420, "errpr_msg": "请输入正确手机号"})
        else:
            rece_obj.cell_phone = data.get('cell_phone')
            result_dict['status']['msg'].append({"cell_phone":"手机号成功修改！"})
        if data.get('province') and data.get('city') and data.get('county') and data.get('specific_address'):
            rece_obj.province = data.get('province')
            rece_obj.city = data.get('city')
            rece_obj.specific_address = data.get('specific_address')
            result_dict['status']['msg'].append({"province/city/specific_address": "地址成功修改！"})
        else:
            result_dict['status']['msg'].append({"error_code": 4420, "errpr_msg": "地址不可为空"})
        rece_obj.save()
        if result_dict['status']['msg']:
            return JsonResponse(result_dict,status=400)
        return JsonResponse({"status":{"code":201,"msg":"修改成功！"}},status=200)

    def delete(self,request):
        request.session['username'] = 'snrsgu'
        data = QueryDict(request.body)
        print(data)
        userid = data.get('userid')
        username = request.session.get('username')
        user = verify_userid(userid, username)
        if not user:
            return JsonResponse({"status": {"code": 400, "msg": {"error_code": 4303, "error_msg": "用户不存在"}}},
                                status=400)
        if user == 'verify':
            return JsonResponse({"status": {"code": 401, "msg": {"error_code": 4303, "error_msg": "没有访问权限"}}},
                                status=401)
        try:
            rece_id = int(data.get('receiving_id'))
        except ValueError:
            return JsonResponse({"status": {"code": 400, "msg": {"error_code": 44422, "error_msg": "收货地址不存在"}}},
                                status=400)
        if rece_id not in [item.id for item in user.receiving_set.all()]:
            return JsonResponse({"status": {"code": 401, "msg": {"error_code": 4303, "error_msg": "没有访问权限"}}},
                                status=401)
        rece_obj = Receiving.objects.get(pk=rece_id)
        rece_obj.delete()
        return JsonResponse({"status":{"code":204,"msg":"删除成功！"}},status=204)