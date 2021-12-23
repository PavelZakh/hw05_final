from django.core.paginator import Paginator

from yatube.settings import PAGE_POSTS_COUNT


def get_page_obj(obj_list, page_num):
    paginator = Paginator(obj_list, PAGE_POSTS_COUNT)
    return paginator.get_page(page_num)
