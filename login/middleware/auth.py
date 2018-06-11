#coding=utf-8
from django.utils.deprecation import MiddlewareMixin


class UserLogin(MiddlewareMixin):

    def process_request(self,request):
        if not request.path.startswith("/admin/"):
            
            print request.path
    def process_view(self, request, callback, callback_args, callback_kwargs):
        pass
    def process_exception(self, request, exception):
        pass

    def process_response(self, request, response):
        print("中间件1返回")
        return response
