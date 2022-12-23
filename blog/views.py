from django.shortcuts import render,redirect, get_object_or_404

from blog.models import BlogPost
from blog.forms import CreateBlogPostForm, UpdateBlogPostForm
from account.models import Account
from django.db.models import Q
from django.http import HttpResponse

# Create your views here.

def create_blog_view(request):
    context={}
    user=request.user  
    if not user.is_authenticated:
        return redirect('must_authenticate')

    form=CreateBlogPostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        obj=form.save(commit=False)  #We dont save immediately because we want to set the author
        author=Account.objects.filter(email=user.email).first() #get first item in the query set returned
        obj.author=author
        obj.save()
        form=CreateBlogPostForm()  # I want to reset everything, i want o set the form to a brand new form

    #Now passing the form to the view
    context['form']=form

    return render(request,'blog/create_blog.html',context)


def detail_blog_view(request,slug):
    context={}

    blog_post=get_object_or_404(BlogPost,slug=slug)
    context['blog_post']=blog_post

    return render(request,'blog/detail_blog.html',context)


def edit_blog_view(request,slug):
    context={}
    user=request.user
    if not user.is_authenticated:
        return redirect('must_authenticate')


    blog_post=get_object_or_404(BlogPost,slug=slug)

    if blog_post.author != user:
        return HttpResponse("You are not the author of this blog post")
    if request.POST:
        form=UpdateBlogPostForm(request.POST or None,request.FILES or None, instance=blog_post)
        if form.is_valid():
            obj=form.save(commit=False)
            obj.save()
            context['success_message']="Success"
            blog_post=obj
    form=UpdateBlogPostForm(
        initial={
            "title":blog_post.title,
            "body":blog_post.body,
            "image":blog_post.image
            }
    )

    context['form']=form
        
    return render(request,'blog/edit_blog.html',context)

#Create a function to get a quesry set based on a particular search

def get_blog_queryset(query=None):
    queryset=[]   #Initialize the queyset to an empty list
    queries=query.split(" ")  #exampl if they search python install 2020=>['python','install','2020']
    for q in queries:
        posts=BlogPost.objects.filter(
            Q(title__icontains=q)|Q(body__icontains=q)
        ).distinct()
    
        for post in posts:
            queryset.append(post)
    return list(set(queryset))  # A set will make sure that its unique


