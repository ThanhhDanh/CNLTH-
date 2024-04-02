from rest_framework import viewsets, generics, status, parsers, permissions
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from courses import serializers, paginators, permission
from courses.models import Category, Course, Lesson, User, Comment, Like


class CategoryViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Category.objects.filter(active=True)
    serializer_class = serializers.CategorySerializer


class CourseViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Course.objects.filter(active=True)
    serializer_class = serializers.CourseSerializer
    pagination_class = paginators.CoursePaginator

    def get_queryset(self):
        queryset = self.queryset

        if self.action.__eq__('list'):
            q = self.request.query_params.get('q')
            if q:
                queryset = queryset.filter(name__icontains=q)

            cate_id = self.request.query_params.get('category_id')
            if cate_id:
                queryset = queryset.filter(category_id=cate_id)

        return queryset

    @action(methods=['get'], url_path='lessons', detail=True)
    def get_lessons(self, request, pk):
        lessons = self.get_object().lesson_set.filter(active=True)

        q = request.query_params.get('q')
        if q:
            lessons = lessons.filter(subject__icontains=q)

        return Response(serializers.LessonSerializer(lessons, many=True).data,
                        status=status.HTTP_200_OK)


class LessonViewSet(viewsets.ViewSet, generics.RetrieveAPIView, generics.ListAPIView):
    queryset = Lesson.objects.prefetch_related('tags').filter(active=True)
    serializer_class = serializers.LessonDetailsSerializer

    # def get_comment(self, request):
    #     queryset =self.queryset
    #     course_id = self.request.query_params.get('course')
    #     if course_id:
    #         queryset = queryset.filter(course_id=course_id)
    #
    #     return queryset

    @action(methods=['get'], url_path='comments', detail=True)
    def get_comments(self, request, pk):
        comments = self.get_object().comment_set.order_by('-id')
        q = request.query_params.get('q')
        if q:
            comments = comments.filter(content__icontains=q)

        #Phân trang cho comment
        paginator = paginators.CommentPaginator()
        page = paginator.paginate_queryset(comments, request)
        if page is not None:
            serializer = serializers.CommentSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        return Response(serializers.CommentSerializer(comments, many=True).data,
                        status=status.HTTP_200_OK)

    def get_permissions(self):
        if self.action in ['add_comment']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return serializers.AuthenticatedLessonDetailsSerializer

        return self.serializer_class

    @action(methods=['post'], url_path='comments',detail=True)
    def add_comment(self, request,pk):
        #Comment.onject.create()
        c = self.get_object().comment_set.create(content = request.data.get("content"), user = request.user)

        return Response(serializers.CommentSerializer(c).data, status=status.HTTP_201_CREATED)


    @action(methods=['post'], url_path = 'like', detail=True)
    def like(self, request, pk):
        like,created = Like.objects.get_or_create(lesson = self.get_object(), user = request.user)
        if not created:
            like.active = not like.active
            like.save()
        return Response(serializers.LessonDetailsSerializer(self.get_object()).data)




class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.UpdateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser, ]
    permission_classes = [permissions.IsAuthenticated]

    #Xác thực User
    def get_permissions(self):
        if self.action in ['get_current_user']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


    @action(methods=['get', 'patch'], url_path='current-user', detail=False) #detail = false là nó sẽ không gửi cái id về
    def get_current_user(self, request):
        user = request.user
        if request.method.__eq__('PATCH'):
            for k, v in request.data.items():
                setattr(user,k,v) #user.firt_name = v
            user.save()
        return Response(serializers.UserSerializer(user).data)


class CommentViewSet(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_class = [permission.CommentOwner]



# class UserView(APIView):
#     authentication_classes = [BasicAuthentication,
#     TokenAuthentication]
#     permission_classes = [IsAdminUser]
#     def get(self, request):
#         pass
#
# class UserAPIView(APIView, viewsets.ViewSet, generics.GenericAPIView):
#
#     def get_user(self, request):
#         # Kiểm tra xem header Authorization có tồn tại không
#         if 'HTTP_AUTHORIZATION' in request.META:
#             auth_header = request.META['HTTP_AUTHORIZATION']
#             # Kiểm tra xem header Authorization có chứa Bearer token không
#             if auth_header.startswith('Bearer '):
#                 access_token = auth_header.split(' ')[1]
#                 # Thực hiện xác thực access_token ở đây
#                 # Nếu access_token hợp lệ, tiếp tục xử lý yêu cầu
#                 # Ví dụ: lấy đối tượng từ database và serialize nó
#                 user = User.objects.filter(active=True)
#                 serializer = serializers.UserSerializer(user)
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#         # Nếu không có hoặc không hợp lệ, trả về lỗi 401 Unauthorized
#         return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

