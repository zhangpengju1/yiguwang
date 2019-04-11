from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from account.views import verify_userid
import time, datetime
from database.models import OrderForm, Specification, OrderCommodity, Claim_receiving
from random import randint


# Create your views here.


class Search(View):
    """
    个人订单条件筛选
    """

    def get(self, request):
        """

        :param request:
        :return:
        """
        data = request.GET
        userid = data.get('userid')
        request.session['username'] = 'snrsgu'  # 测试使用日后注释
        username = request.session.get('username')
        user = verify_userid(userid, username)
        if not user:
            return JsonResponse({"status": {"code": 400, "msg": {"error_code": 4303, "error_msg": "用户不存在"}}},
                                status=400)
        if user == 'verify':
            return JsonResponse({"status": {"code": 401, "msg": {"error_code": 4303, "error_msg": "没有查询权限"}}},
                                status=401)
        condition = {'num': data.get('num'),
                     'status': data.get('status'),
                     'start': data.get('start'),
                     'end': data.get('end')}
        condition = {i: condition[i] for i in condition if condition[i]}  # 将筛选条件为空的键值对删掉
        order_set = user.orderform_set.all()
        if 'num' in condition.keys():
            order_set = order_set.filter(num=condition['num'])
        if 'status' in condition.keys():
            order_set = order_set.filter(num=condition['status'])
        if 'start' in condition.keys():
            set_ = []
            for item in order_set:
                if not float(item.order_time) < float(condition['start']):
                    set_.append(item)
            order_set = set_
        if 'end' in condition.keys():
            set_ = []
            for item in order_set:
                if not float(item.order_time) > float(condition['end']):
                    set_.append(item)
            order_set = set_
        result_dict = {"status": {"code": 200, "msg": "ok"}, "data": []}
        for item in order_set:
            result_dict['data'].append({
                "id": item.pk,
                "order": item.num,
                "amount": item.gross_amount,
                "freight": item.freight,
                "freight_time": item.freight_time,
                "order_status": item.status,
                "order_time": item.order_time,
            })

        return JsonResponse(result_dict, status=200)


class Indent(View):
    """我的订单操作"""

    def ordercommodity(self, commodity_dict):
        """

        :param commodity_dict:[{"id1":1,"num":2},{"id1":1,"num":2}]
        :return:[(obj,1),(obj,2)]
        """
        result_list = []
        for item in commodity_dict:
            comm_obj = Specification.objects.get(pk=item['id'])
            result_list.append((comm_obj, int(item['num'])))
        return result_list

    def get(self, request):
        """
        订单的默认展示，
        必传参数userid
        可选参数：recently 0或1或不传（False)
        :param request:
        :return:
        """
        data = request.GET
        userid = data.get('userid')
        request.session['username'] = 'snrsgu'  # 测试使用日后注释
        username = request.session.get('username')
        user = verify_userid(userid, username)
        if not user:
            return JsonResponse({"status": {"code": 400, "msg": {"error_code": 4303, "error_msg": "用户不存在"}}},
                                status=400)
        if user == 'verify':
            return JsonResponse({"status": {"code": 401, "msg": {"error_code": 4303, "error_msg": "没有查询权限"}}},
                                status=401)
        result_dict = {"status": {"code": 200, "msg": "ok"}, "data": []}
        bool_ = data.get('recently')
        if bool_:  # 如果传入了参数recently
            try:
                int(bool_)  # 转换成整数
            except ValueError:
                return JsonResponse(
                    {"status": {"code": 401, "msg": {"error_code": 4303, "error_msg": "recently参数只支持整数"}}},
                    status=401)
            else:  # 如果转换成功
                if bool_:  # 判断真假，如果为真则返回近三月的所有订单情况
                    # 返回三个月前的首日时间戳
                    hour_time = int(time.mktime(
                        datetime.date(datetime.date.today().year, datetime.date.today().month - 3, 1).timetuple()))
                    order_set = user.orderform_set.all()
                    for item in order_set[:300]:
                        if float(item.order_time) >= hour_time:  # 判断订单时间在近三月内
                            result_dict['data'].append({
                                "id": item.pk,
                                "order": item.num,
                                "amount": item.gross_amount,
                                "freight": item.freight,
                                "freight_time": item.freight_time,
                                "order_status": item.status,
                                "order_time": item.order_time,
                            })
                    return JsonResponse(result_dict, status=200)
        # 如果查询全部订单
        order_set = user.orderform_set.all()
        for item in order_set:
            result_dict['data'].append({
                "id": item.pk,
                "order": item.num,
                "amount": item.gross_amount,
                "freight": item.freight,
                "freight_time": item.freight_time,
                "order_status": item.status,
                "order_time": item.order_time,
            })
        return JsonResponse(result_dict, status=200)

    def post(self, request):
        """
        生成订单
        非自提参数：userid、commodity[{id1":1,"num":2},{"id1":1,"num":2}]、paymode付款方式
        receiving收货地址id、note备注
        自提参数：userid、commodity[{id1":1,"num":2},{"id1":1,"num":2}]、paymode付款方式
        is_self=1、claim_addr取货地址id、claim_name取货名、phon联系方式
        :param request:
        :return:
        """
        data = request.POST
        userid = data.get('userid')
        request.session['username'] = 'snrsgu'  # 测试使用日后注释
        username = request.session.get('username')
        user = verify_userid(userid, username)
        if not user:
            return JsonResponse({"status": {"code": 400, "msg": {"error_code": 4303, "error_msg": "用户不存在"}}},
                                status=400)
        if user == 'verify':
            return JsonResponse({"status": {"code": 401, "msg": {"error_code": 4303, "error_msg": "请先登录"}}},
                                status=401)
        # 以下是自提
        is_self = data.get('is_self')  # 是否自提
        try:
            commodity_dict = eval(data.get('commodity'))  # 商品json
        except (SyntaxError,NameError,TypeError):
            return JsonResponse(
                {"status": {"code": 401, "msg": {"error_code": 4303,
                                                 "error_msg": '商品信息有误请准确传入类似[{"id":商品id,"num":购买数量},{"id":商品id,"num":购买数量}]的字符串'}}},
                status=401)
        paymode = data.get('paymode')  # 付款方式
        if not paymode in '12345':
            return JsonResponse({"status": {"code": 401, "msg": {"error_code": 4303, "error_msg": "付款方式有误"}}},
                                status=401)
        if is_self:  # 如果传入了参数is_self
            try:
                is_self = int(is_self)  # 转换成整数
            except ValueError:
                return JsonResponse(
                    {"status": {"code": 401, "msg": {"error_code": 4303, "error_msg": "is_self参数只支持整数"}}},
                    status=401)
            else:
                if is_self:  # 如果为真则为是自提的情况下
                    claim_addr = data.get('claim_addr')  # 取货id
                    try:
                        rece_obj = Claim_receiving.objects.get(pk=claim_addr)  # 取货地址对象
                    except Claim_receiving.DoesNotExist:
                        return JsonResponse(
                            {"status": {"code": 401, "msg": {"error_code": 4303, "error_msg": "取货信息有误"}}},
                            status=401)
                    temp_subtotal = {}  # 临时小计字典
                    # {'1':'32.2','2':'43'}
                    order_result = self.ordercommodity(commodity_dict)  # [(商品对象,购买数量),(商品对象,购买数量)]
                    for i in order_result:
                        temp_subtotal.update(
                            {i[0].id: i[0].mall_price * i[1]})  # 向临时小计字典添加商品id和该商品的总价 {'1':'32.2','2':'43'}
                    subtotal = 0  # 所有商品总价之和
                    for value in temp_subtotal.values():
                        subtotal += value
                    claim_name = data.get('claim_name')  # 取货名称
                    phone = data.get('phon')  # 取货电话
                    note = data.get('note')  # 备注
                    subtotal = float(subtotal) + 8.00
                    if not claim_name:
                        return JsonResponse(
                            {"status": {"code": 401, "msg": {"error_code": 4303, "error_msg": "取货名称不可为空"}}},
                            status=401)
                    if not phone:
                        return JsonResponse(
                            {"status": {"code": 401, "msg": {"error_code": 4303, "error_msg": "联系手机不可为空"}}},
                            status=401)
                    orderform = OrderForm.objects.create(user=user,  # 订单绑定的用户对象
                                                         num=str(
                                                             time.strftime("%Y%m%d%H%M%S",
                                                                           time.localtime(time.time()))) + str(
                                                             randint(100, 999)),  # 订单编号，当前时间（精确到秒）加100-999的随机数
                                                         order_time=time.time(), paymode=paymode, freight=8.00,
                                                         # 邮费默认为八元
                                                         gross_amount=float(subtotal), claim_addr=rece_obj.claim_addr,
                                                         claim_name=claim_name, phone=phone, note=note,is_self=True)
                    for i in order_result:
                        OrderCommodity.objects.create(orderform=orderform, specification=i[0], quantity=i[1],
                                                      subtotal=i[0].mall_price * int(i[1]))  # 多对多表中创建于订单的关联，创建与多个商品的关联
                    return JsonResponse({"status": {"code": 200, "msg": "订单提交成功！"}}, status=200)
        # 非自提情况下
        receiving = data.get('receiving')  # 收货地址id
        rece_obj_set = user.receiving_set.filter(pk=receiving)  # 收货地址对象
        if not rece_obj_set:  # 如果该收货地址不属于现在登录的用户
            return JsonResponse({"status": {"code": 401, "msg": {"error_code": 4303, "error_msg": "该收货地址没有查询权限"}}},
                                status=401)
        temp_subtotal = {}
        # {'1':'32.2','2':'43'}
        order_result = self.ordercommodity(commodity_dict)  # [(obj,1),(obj,2)]
        for i in order_result:
            temp_subtotal.update({i[0].id: i[0].mall_price * int(i[1])})
        subtotal = 0
        for value in temp_subtotal.values():
            subtotal += value
        rece_obj = rece_obj_set[0]
        receive_name = rece_obj.name
        district = rece_obj.province + rece_obj.city + rece_obj.district
        details_addr = rece_obj.detailed
        note = data.get('note')  # 备注
        subtotal = float(subtotal) + 8.00
        orderform = OrderForm.objects.create(user=user,
                                             num=str(
                                                 time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))) + str(
                                                 randint(100, 999)),
                                             order_time=time.time(), paymode=paymode, freight=8.00,
                                             phone=rece_obj.cell_phone,
                                             gross_amount=float(subtotal),
                                             receive_name=receive_name, district=district,
                                             details_addr=details_addr, note=note, ship_mode='依谷网协调配送')
        for i in order_result:
            specification = OrderCommodity.objects.create(orderform=orderform, specification=i[0],
                                                          quantity=i[1],
                                                          subtotal=i[0].mall_price * int(i[1]))
        return JsonResponse({"status": {"code": 200, "msg": "订单提交成功！"}}, status=200)


class Details(View):
    def get(self, request):
        """
        订单详情查询
        userid、num订单号
        :param request:
        :return:
        """
        data = request.GET
        userid = data.get('userid')
        request.session['username'] = 'snrsgu'
        username = request.session.get('username')
        user = verify_userid(userid, username)
        if not user:
            return JsonResponse({"status": {"code": 400, "msg": {"error_code": 4303, "error_msg": "用户不存在"}}},
                                status=400)
        if user == 'verify':
            return JsonResponse({"status": {"code": 401, "msg": {"error_code": 4303, "error_msg": "没有查询权限"}}},
                                status=401)
        try:
            orde_obj = user.orderform_set.get(num=data.get('num'))
        except OrderForm.DoesNotExist:
            return JsonResponse({"status": {"code": 401, "msg": {"error_code": 4303, "error_msg": "没有查询权限"}}},
                                status=401)
        result_dict = {
            "status": {"code": 200, "msg": "ok"},
            "data": {
                "my_order": {
                    "orderid": orde_obj.num,
                    "username": orde_obj.user.email,
                    "order_time": orde_obj.order_time,
                    "status": orde_obj.get_status_display(),
                    "paymode": orde_obj.get_paymode_display(),
                    "ship_mode": orde_obj.ship_mode,
                    "order_way": orde_obj.order_way,
                    "pay_status": orde_obj.pay_status,
                    "delivery_num": orde_obj.delivery_num
                },
                "order_detail": {
                    "goods_list": [],
                    "total": {
                        "freight": orde_obj.freight,
                        "payment_amount": orde_obj.gross_amount,
                        "order_price": orde_obj.gross_amount - orde_obj.freight
                    }
                },
                "logistics": {
                    "receive_name": orde_obj.receive_name,
                    "phone": orde_obj.phone,
                    "district": orde_obj.district,
                    "details_addr": orde_obj.details_addr,
                    "note": orde_obj.note,
                    "freight_time": orde_obj.freight_time
                }
            }
        }
        for i in orde_obj.ordercommodity_set.all():
            goods_dice = {
                "goods_type": "个人精选",
                "name": i.specification.name,
                "brand": i.specification.commodity.brand.name,
                "describe": i.specification.describe,
                "price": i.specification.mall_price,
                "num": i.quantity,
                "subtotal": i.subtotal
            }
            result_dict['data']["order_detail"]["goods_list"].append(goods_dice)
        if orde_obj.is_self == True:
            result_dict['data']['logistics'] = {
                "claim_name": orde_obj.claim_name,
                "phone": orde_obj.phone,
                "claim_addr": orde_obj.claim_addr,
                "note": orde_obj.note
            }
            del result_dict['data']['my_order']['ship_mode']
        return JsonResponse(result_dict, status=200)
