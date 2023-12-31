from django.shortcuts import render, redirect
from django.http import HttpResponse
import markdown
# 引入刚才定义的ArticlePostForm表单类
from .forms import ArticlePostForm
# 引入User模型
from django.contrib.auth.models import User

from .models import ArticlePost

# Create your views here.
def article_list(request):
    
    articles = ArticlePost.objects.all()
    context = {'articles':articles}

    return render(request, 'article/list.html', context)

# 文章详情
def article_detail(request, id):
    article = ArticlePost.objects.get(id=id)

    # 将markdown语法渲染成html样式
    article.body = markdown.markdown(article.body,
        extensions=[
        # 包含 缩写、表格等常用扩展
        'markdown.extensions.extra',
        # 语法高亮扩展
        'markdown.extensions.codehilite',
        ])

    context = { 'article': article }
    return render(request, 'article/detail.html', context)

# 写文章的视图
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
            new_article.author = User.objects.get(id=1)
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
        # 赋值上下文
        context = { 'article_post_form': article_post_form }
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

def article_update(request, id):
    """
    更新文章的视图函数
    通过POST方法提交表单，更新titile、body字段
    GET方法进入初始表单页面
    id： 文章的 id
    """
    article = ArticlePost.objects.get(id=id)

    if request.method == 'POST':
        article_post_form = ArticlePostForm(data=request.POST)

        if article_post_form.is_valid():
            article.title = request.POST['title']
            article.body = request.POST['body']
            article.save()

            return redirect("article:article_detail",id=id)
        
        else:

            return HttpResponse("提交的表单有误，请重新填写。")
    else:
        article_post_form = ArticlePostForm()
        context = {'article':article, 'article_post_form':article_post_form}

        return render(request, 'article/update.html', context)