from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
import markdown
from django.contrib.auth.decorators import login_required
# 引入刚才定义的ArticlePostForm表单类
from .forms import ArticlePostForm
# 引入User模型
from django.contrib.auth.models import User, AnonymousUser
from django.core.paginator import Paginator
from django.db.models import Q

from .models import ArticlePost, ArticleColumn
from comment.models import Comment

# Create your views here.
def article_list(request):

    search = request.GET.get('search')
    order = request.GET.get('order')
    if search:
        if order == 'total_views':
            article_list = ArticlePost.objects.filter(
                Q(title__icontains = search) |
                Q(body_icontains = search)
            ).order_by('-total_views')
        else:
            article_list = ArticlePost.objects.filter(
                Q(title__icontains=search) |
                Q(body__icontains=search)
            )
    else:
        search = ''
        if order == 'total_views':
            article_list = ArticlePost.objects.all().order_by('-total_views')
        else:
            article_list = ArticlePost.objects.all()
    
    paginator = Paginator(article_list, 3)
    page = request.GET.get('page')
    articles = paginator.get_page(page)

    context = { 'articles': articles, 'order': order, 'search': search }
    
    return render(request, 'article/list.html', context)


# 文章详情
def article_detail(request, id):
    article = get_object_or_404(ArticlePost, id=id)
    comments = Comment.objects.filter(article=id)

    if not isinstance(request.user, AnonymousUser) and request.user != article.author:
        # 只统计已登录用户（不包括作者本人）
        article.total_views += 1
        article.save(update_fields=['total_views'])
    print(request.user)

    md = markdown.Markdown(
        extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        ]
    )
    article.body = md.convert(article.body)

    # 新增了md.toc对象
    context = { 'article': article, 'toc': md.toc , 'comments': comments}

    return render(request, 'article/detail.html', context)

# 写文章的视图
@login_required(login_url='/userprofile/login/')
def article_create(request):
    # 判断用户是否提交数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存数据，但暂时不提交到数据库中
            new_article = article_post_form.save(commit=False)
            # 指定数据库中 id=1 的用户为作者
            new_article.author = User.objects.get(id=request.user.id)
            # 设置栏目
            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            # 将新文章保存到数据库中
            new_article.save()
            # 完成后返回到文章列表
            return redirect("article:article_list")
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果用户请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()

        columns = ArticleColumn.objects.all()
        # 赋值上下文
        context = { 'article_post_form': article_post_form, 'columns':columns }
        # 返回模板
        return render(request, 'article/create.html', context)
    
# def article_delete(request, id):
        
#     article = ArticlePost.objects.get(id=id)
#     article.delete()

#     return redirect("article:article_list")

def article_safe_delete(request, id):
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        article.delete()
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许post请求")

@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    """
    更新文章的视图函数
    通过POST方法提交表单，更新titile、body字段
    GET方法进入初始表单页面
    id： 文章的 id
    """
    article = ArticlePost.objects.get(id=id)

    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")
    
    if request.method == 'POST':
        article_post_form = ArticlePostForm(data=request.POST)

        if article_post_form.is_valid():
            article.title = request.POST['title']
            article.body = request.POST['body']
            if request.POST['column'] != 'none':
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column =  None
            article.save()

            return redirect("article:article_detail",id=id)
        
        else:

            return HttpResponse("提交的表单有误，请重新填写。")
    else:
        article_post_form = ArticlePostForm()
        columns =ArticleColumn.objects.all()
        context = {'article':article, 
                   'article_post_form':article_post_form,
                   'columns':columns}

        return render(request, 'article/update.html', context)