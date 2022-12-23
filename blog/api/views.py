from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from rest_framework.authentication import TokenAuthentication

from rest_framework.filters import SearchFilter,OrderingFilter

from account.models import Account
from blog.models import BlogPost
from blog.api.serializers import BlogPostSerializer
from blog.api.serializers import BlogPostUpdateSerializer

from blog.api.serializers import BlogPostCreateSerializer

CREATE_SUCCESS = 'created'

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def api_detail_blog_view(request,slug):
    try:
        blog_post=BlogPost.objects.get(slug=slug)

    except BlogPost.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method=='GET':
        serializer=BlogPostSerializer(blog_post)
        return Response(serializer.data)

# @api_view(['PUT',])
# @permission_classes((IsAuthenticated,))
# def api_update_blog_view(request,slug):
#     #First get the blog post
#     try:
#         blog_post=BlogPost.objects.get(slug=slug)

#     except BlogPost.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
    
#     user=request.user
#     if blog_post.author != user:
#         return Response({'response':"You dont have permission to edit that"})

#     if request.method=='PUT':
#         serializer=BlogPostSerializer(blog_post, data=request.data)
#         data={}
#         if serializer.is_valid():
#             serializer.save()
#             data['success']="Update Successful"
#             return Response(data=data)
#         return Response(serializer.errors,status.HTTP_400_BAD_REQUEST)

# Response: https://gist.github.com/mitchtabian/32507e93c530aa5949bc08d795ba66df
# Url: https://<your-domain>/api/blog/<slug>/update
# Headers: Authorization: Token <token>
@api_view(['PUT',])
@permission_classes((IsAuthenticated,))
def api_update_blog_view(request, slug):

	try:
		blog_post = BlogPost.objects.get(slug=slug)
	except BlogPost.DoesNotExist:
		return Response(status=status.HTTP_404_NOT_FOUND)

	user = request.user
	if blog_post.author != user:
		return Response({'response':"You don't have permission to edit that."}) 
		
	if request.method == 'PUT':
		serializer = BlogPostUpdateSerializer(blog_post, data=request.data, partial=True)  #Partial=true gives permission to update only some of the fiedlds
		data = {}
		if serializer.is_valid():
			serializer.save()
			data['response'] = "UPDATE_SUCCESS"
			data['pk'] = blog_post.pk
			data['title'] = blog_post.title
			data['body'] = blog_post.body
			data['slug'] = blog_post.slug
			data['date_updated'] = blog_post.date_updated
			image_url = str(request.build_absolute_uri(blog_post.image.url))
			if "?" in image_url:
				image_url = image_url[:image_url.rfind("?")]
			data['image'] = image_url
			data['username'] = blog_post.author.username
			return Response(data=data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def api_is_author_of_blogpost(request, slug):
	try:
		blog_post = BlogPost.objects.get(slug=slug)
	except BlogPost.DoesNotExist:
		return Response(status=status.HTTP_404_NOT_FOUND)

	data = {}
	user = request.user
	if blog_post.author != user:
		data['response'] = "You don't have permission to edit that."
		return Response(data=data)
	data['response'] = "You have permission to edit that."
	return Response(data=data)



@api_view(['DELETE',])
@permission_classes((IsAuthenticated,))
def api_delete_blog_view(request,slug):
    try:
        blog_post=BlogPost.objects.get(slug=slug)

    except BlogPost.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user=request.user
    if blog_post.author != user:
        return Response({'response':"You dont have permission to delete that"})

    if request.method=='DELETE':
        operation=blog_post.delete()
        data={}
        if operation:
            data["success"]="Delete Successful"
        else:
            data["failure"]="Delete Failed"
        return Response(data=data)

# @api_view(['POST',])
# @permission_classes((IsAuthenticated,))
# def api_create_blog_view(request):

#     # account=Account.objects.get(pk=1)
#     # blog_post=BlogPost(author=account)

#     account=request.user
#     blog_post=BlogPost(author=account)

#     if request.method=='POST':
#         serializer=BlogPostSerializer(blog_post,data=request.data) #We are passing the blogpost that has an author already attached to it
#         data={}
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data,status=status.HTTP_201_CREATED)
#         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)




# Response: https://gist.github.com/mitchtabian/78d7dcbeab4135c055ff6422238a31f9
# Url: https://<your-domain>/api/blog/create
# Headers: Authorization: Token <token>
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def api_create_blog_view(request):

	if request.method == 'POST':

		data = request.data
		data['author'] = request.user.pk
		serializer = BlogPostCreateSerializer(data=data)

		data = {}
		if serializer.is_valid():
			blog_post = serializer.save()
			data['response'] = CREATE_SUCCESS
			data['pk'] = blog_post.pk
			data['title'] = blog_post.title
			data['body'] = blog_post.body
			data['slug'] = blog_post.slug
			data['date_updated'] = blog_post.date_updated
			image_url = str(request.build_absolute_uri(blog_post.image.url))
			if "?" in image_url:
				image_url = image_url[:image_url.rfind("?")]
			data['image'] = image_url
			data['username'] = blog_post.author.username
			return Response(data=data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#We will be using class based views
class ApiBlogListView(ListAPIView):
    queryset=BlogPost.objects.all()
    serializer_class=BlogPostSerializer
    authentication_classes=(TokenAuthentication,)
    permission_classes=(IsAuthenticated,)
    pagination_class=PageNumberPagination
    filter_backends=(SearchFilter,OrderingFilter)
    search_fields=['title','body','author__username']






