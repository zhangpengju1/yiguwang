from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class TimeTransition:
    def time(self,timestamp):
        import time
        try:
            st = time.localtime(float(timestamp))
        except (TypeError,ValueError):
            return False
        return time.strftime('%Y-%m-%d %H:%M:%S',st)

class UserProfile(models.Model):
    """
    用户信息拓展
    """
    head_portrait = models.ImageField(upload_to='user/head_portrait/')
    cell_phone = models.CharField(max_length=11, null=True, verbose_name='手机号')
    sex_choice = ((1, '男'), (0, '女'), (2, '密'))
    sex = models.PositiveSmallIntegerField(choices=sex_choice, verbose_name='性别')
    birthday = models.DateField(null=True, verbose_name='生日')
    wechat = models.CharField(max_length=20, null=True, verbose_name='微信')
    qq = models.CharField(max_length=15, null=True, verbose_name='QQ')
    msn = models.CharField(max_length=20, null=True, verbose_name='MSN')
    work_unit = models.CharField(max_length=50, null=True, verbose_name='工作单位')
    family_address = models.CharField(max_length=50, null=True, verbose_name='家庭住址')
    balance = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='账户余额')
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Transaction(models.Model,TimeTransition):
    """
    用户交易记录
    """
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    odd = models.CharField(max_length=20, verbose_name='交易单号')
    amount = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='交易金额')
    trding_hour = models.CharField(max_length=30, verbose_name='交易时间戳')

    def __str__(self):
        return self.odd


class Category(models.Model):
    """
    商品分类
    """
    name = models.CharField(max_length=20, verbose_name='分类名称')
    desc = models.CharField(max_length=50, verbose_name='分类描述')
    parent = models.ForeignKey('self', default=0, null=True, blank=True, related_name='children', verbose_name='上级分类',
                               limit_choices_to={'is_abort': False, 'is_root': True}, on_delete=models.CASCADE)
    is_root = models.BooleanField(default=False, verbose_name='是否是一级分类')
    image = models.ImageField(upload_to='commodity/category/', verbose_name='分类图片', null=True, blank=True)
    is_abort = models.BooleanField(default=False, verbose_name='是否删除')

    def __str__(self):
        return self.name


class Brand(models.Model):
    """
    商品品牌
    """
    name = models.CharField(max_length=20, verbose_name='品牌名称')

    def __str__(self):
        return self.name


class Commodity(models.Model):
    """
    商品
    """
    name = models.CharField(max_length=50, verbose_name='商品名称')
    origin = models.CharField(max_length=30, null=True, verbose_name='产地')
    status_choices = ((1, '上架'), (2, '下架'), (3, '促销'), (4, '预售'))
    status = models.PositiveSmallIntegerField(choices=status_choices, default=1, verbose_name='产品销售状态')
    inventory = models.PositiveIntegerField(default=0, verbose_name='商品库存')
    sales = models.PositiveIntegerField(default=0, verbose_name='商品销量')
    comment_num = models.PositiveIntegerField(default=0, verbose_name='评论数量')
    brand = models.ForeignKey(Brand, on_delete=models.DO_NOTHING, null=True, verbose_name='关联品牌')

    def __str__(self):
        return self.name


class Collect(models.Model):
    """
    用户收藏商品
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='关联用户')
    commodity = models.ForeignKey(Commodity, on_delete=models.DO_NOTHING, verbose_name='关联商品')

    def __str__(self):
        return (self.user.username, self.commodity.name)


class Comment(models.Model,TimeTransition):
    """
    商品评论
    """
    user = models.ForeignKey(UserProfile, on_delete=models.DO_NOTHING, verbose_name='关联用户')
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, verbose_name='关联商品')
    reply = models.ForeignKey('self', null=True, blank=True, on_delete=models.DO_NOTHING, verbose_name='关联回复')
    time = models.CharField(max_length=30, verbose_name='评论时间戳')
    content = models.CharField(max_length=150, verbose_name='评论内容')

    def __str__(self):
        return self.content


class Specification(models.Model):
    """
    商品规格
    """
    name = models.CharField(max_length=100, verbose_name='商品规格全称')
    describe = models.CharField(max_length=20, verbose_name='规格描述')
    integral = models.PositiveSmallIntegerField(default=0, verbose_name='商品积分')
    mall_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='商城价')
    market_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='市场价')
    inventory = models.PositiveIntegerField(default=0, verbose_name='该规格商品的库存数量')
    sales_volume = models.PositiveIntegerField(default=0, verbose_name='该规格商品的销量')
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, verbose_name='关联商品')

    def __str__(self):
        return self.name


class CommodityImage(models.Model):
    """
    商品图片
    """
    image = models.ImageField(upload_to='commodity/infoimage/', verbose_name='商品信息图片')
    is_show = models.BooleanField(default=1, verbose_name='是否为展示图片')
    num = models.PositiveSmallIntegerField(verbose_name='图片编号')
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, verbose_name='关联商品')


class Cart(models.Model):
    """
    购物车
    """
    commodity = models.ManyToManyField(Specification)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(verbose_name='购买数量')

    def __str__(self):
        return self.commodity.name


class OrderForm(models.Model,TimeTransition):
    """
    订单
    """
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    num = models.CharField(max_length=25, verbose_name='订单编号')
    status_choices = ((1, '待支付'), (2, '代发货'), (3, '待收货'), (4, '已收货'), (5, '已确认'), (6, '已完成'), (0, '已取消'))
    status = models.PositiveSmallIntegerField(choices=status_choices, verbose_name='订单状态')
    order_time = models.CharField(max_length=30, verbose_name='下单时间戳')
    delivery_time = models.CharField(max_length=30, null=True, verbose_name='发货时间戳')
    receipt_time = models.CharField(max_length=30, null=True, verbose_name='收货时间戳')
    freight = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='邮费')
    gross_amount = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='订单总价')
    paymode_choices = ((1, '余额支付'), (2, '支付宝支付'), (3, '微信支付'), (4, '银联支付'), (5, '广发银行'))
    paymode = models.PositiveSmallIntegerField(choices=paymode_choices, verbose_name='支付方式')
    address = models.CharField(max_length=150, verbose_name='省/市/区')
    detailed = models.CharField(max_length=150, verbose_name='详细地址')
    is_self = models.BooleanField(default=0, verbose_name='是否自提')

    def __str__(self):
        return self.num


class Receiving(models.Model):
    """
    收货信息
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=10, verbose_name='收货名')
    cell_phone = models.CharField(max_length=11, verbose_name='手机号')
    postal_code = models.CharField(max_length=6, null=True, verbose_name='邮政编码')
    province = models.CharField(max_length=20, null=True, verbose_name='省')
    city = models.CharField(max_length=20, null=True, verbose_name='市')
    district = models.CharField(max_length=20, null=True, verbose_name='区/县/乡镇')
    detailed = models.CharField(max_length=150, verbose_name='详细地址')
    phone = models.CharField(max_length=30, null=True, verbose_name='固定电话')
    is_default = models.BooleanField(default=0, verbose_name='默认地址')

    def __str__(self):
        return self.name


class OrderCommodity(models.Model):
    """
    订单与商品进行多对多的关联，中间数据表
    """
    orderform = models.ForeignKey(OrderForm, on_delete=models.DO_NOTHING)
    commodity = models.ForeignKey(Commodity, on_delete=models.DO_NOTHING)
    quantity = models.PositiveSmallIntegerField(default=1, verbose_name='商品的选购数量，默认为1')
    subtotal = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='商品小计总价')

    def __str__(self):
        return self.quantity