import datetime
import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import View
# from django.views.decorators.csrf import csrf_exempt
from database.models import User, Commodity, Specification, Cart

# Create your views here.


class CartView(View):
    """
    购物车 视图
    """
    @staticmethod
    def get_model_obj(model_name, primary_k):
        """
        通过传入model名字、pk值，在model中通过pk获取model对象，如果没有获取到，返回None
        :param model_name:
        :param primary_key:
        :return:
        """
        try:
            model_obj = model_name.objects.get(pk=primary_k)
        except model_name.DoesNotExist:
            model_obj = None
        return model_obj

    @staticmethod
    def json_response(status_code, error_code=None,
                      error_msg=None, msg=None):
        if error_code is not None:
            result = {
                'status': status_code,
                'msg': {
                    'error_code': error_code,
                    'error_msg': error_msg
                }
            }
            return JsonResponse(result)
        if msg is not None:
            result = {
                'status': status_code,
                'msg': msg
            }
            return JsonResponse(result)

    def getCartListFromCookie(self, request):
        pass

    def get(self, request):
        return HttpResponse('hello')

    def post(self, request):
        """
        用post请求方法，将商品加入购物车
        用户未登录时，将购物车写入Cookie；用户如果已登录，将购物车合并到用户购物车；
        :param request:
        :return:
        """
        req_info = request.POST
        commodity_id = req_info.get('commodityid', None)    # 获取商品id
        commodity_obj = self.get_model_obj(Commodity, primary_k=commodity_id)    # 通过id获取商品对象
        if commodity_obj is None:    # 如果商品id不存在
            res_info = self.json_response(400, error_code=4452, error_msg='商品ID不存在')
            return res_info

        specification_id = req_info.get('specificationid', None)    # 获得商品规格id
        specification_obj = self.get_model_obj(Specification, primary_k=specification_id)  # 通过id获取商品规格对象
        if specification_obj is None:
            res_info = self.json_response(400, error_code=4453, error_msg='商品规格ID不存在')
            return res_info

        quantity = req_info.get('quantity', None)    # 获取商品数量
        try:
            quantity = int(quantity)    # 将商品数量转换为整数
        except ValueError:          # 当商品数量为浮点类型时
            res_info = self.json_response(400, error_code=4454, error_msg='商品数量不能转换为整数')
            return res_info

        except TypeError:           # 当商品数量参数类型错误时
            res_info = self.json_response(400, error_code=4454, error_msg='商品数量类型错误')
            return res_info

        if quantity > specification_obj.inventory:    # 判断请求的商品数量与该规格商品库存的数量
            res_info = self.json_response(400, error_code=4454, error_msg='商品数量过大')
            return res_info

        user_id = req_info.get('userid', None)    # 获取请求参数中的 user_id
        if user_id is not None:    # 如果 请求中带有 user_id，即用户可能已登录
            user_obj = self.get_model_obj(User, primary_k=user_id)  # 通过user_id获取用户对象；
            if user_obj is None:
                res_info = self.json_response(400, error_code=4451, error_msg='用户ID不存在')
                return res_info

            # 这块验证用户是否已登录
            try:
                sess_user = request.session['user_id']
            except KeyError:        # 如果session里面没有user_id的key时，用户一定没有登录
                res_info = self.json_response(400, error_code=4451, error_msg='没有用户登录')
                return res_info

            if sess_user != user_id:
                res_info = self.json_response(400, error_code=4451, error_msg='该用户ID尚未登录')
                return res_info
            # 将商品添加到数据库中

        if user_id is None:    # 请求没有传user_id，表示未登录，将商品添加到Cookie中
            cart1 = request.COOKIES.get('cart1', None)    # 在COOKIES中查找key为cart1的购物车
            if cart1 is None:   # 如果没有key为cart1的COOKIE
                res_info = self.json_response(201, msg='添加购物车成功')
                cart_value = {
                    specification_id: quantity
                }
                cart_value_json = json.dumps(cart_value)
                expires_time = datetime.datetime.now() + datetime.timedelta(days=15)
                res_info.set_cookie(key='cart1', value=cart_value_json, expires=expires_time)
                return res_info
        return HttpResponse('添加到Cookie')

