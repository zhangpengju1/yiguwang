from django.shortcuts import render
from django.http import JsonResponse,HttpResponse,Http404
from django.core import serializers
from django.core.paginator import InvalidPage, Paginator
from haystack.views import SearchView
# Create your views here.

class YiGuView(SearchView):
    def build_page(self):
        """
        Paginates the results appropriately.

        In case someone does not want to use Django's built-in pagination, it
        should be a simple matter to override this method to do what they would
        like.
        """
        try:
            page_no = int(self.request.GET.get('page', 1))
        except (TypeError, ValueError):
            raise Http404("Not a valid number for page.")

        if page_no < 1:
            raise Http404("Pages should be 1 or greater.")

        start_offset = (page_no - 1) * self.results_per_page
        self.results[start_offset:start_offset + self.results_per_page]

        paginator = Paginator(self.results, self.results_per_page)

        try:
            global page
            page = paginator.page(page_no)
        except InvalidPage:
            raise Http404("No such page!")

        return (paginator, page)
    def create_response(self):
        context = super().get_context()
        now_page = self.request.GET.get('page', 1)
        keyword = self.request.GET.get('q',None)
        if not keyword:
            return JsonResponse(
                {
                    "status": {
                        "code": 400,
                        "msg": {
                            "error_code": 4450,
                            "error_msg": "关键字错误"
                        }
                    }
                }
            )
        content = \
            {
            "status": {
                "code": 200,
                "msg": "ok"
            },
            "data": {
                "page": now_page,
                "is_next_page":page.has_next(),
                "sort": '默认排序',
                "goods":
                    [
                        {
                            'name': i.object.name, 'description': i.object.description, 'id': i.object.id,
                            'brand': i.object.commodity.brand, 'describe': i.object.describe,
                            'integral': i.object.integral,
                            'mall_price': i.object.mall_price, 'market_price': i.object.market_price,
                            'inventory': i.object.inventory, 'sales_volume': i.object.sales_volume,
                            'show_image': i.object.commodityimage_set.all()[0].image.url
                        }
                        for i in context['page'].object_list
                    ]
            }
        }
        return JsonResponse(content)


