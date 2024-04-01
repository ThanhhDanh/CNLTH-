from rest_framework import viewsets, generics, status, parsers, permissions
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from courses import serializers, paginators
from courses.models import Category, Course, Lesson, User, Comment


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

    def get_queryset(self):
        queryset =self.queryset
        course_id = self.request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        return queryset

    @action(methods=['get'], url_path='comments', detail=True)
    def get_comments(self, request, pk):
        comments = self.get_object().comment_set.filter(active=True)

        q = request.query_params.get('q')
        if q:
            comments = comments.filter(content__icontains=q)

        return Response(serializers.CommentSerializer(comments, many=True).data,
                        status=status.HTTP_200_OK)


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser, ]
    permission_classes = [permissions.IsAuthenticated]


class CommentViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = Comment.objects.filter(active=True)
    serializer_class = serializers.CommentSerializer


# class UserView(APIView):
#     authentication_classes = [BasicAuthentication,
#     TokenAuthentication]
#     permission_classes = [IsAdminUser]
#     def get(self, request):
#         pass

class UserAPIView(APIView, viewsets.ViewSet, generics.ListAPIView):

    def get(self, request):
        # Kiểm tra xem header Authorization có tồn tại không
        if 'HTTP_AUTHORIZATION' in request.META:
            auth_header = request.META['HTTP_AUTHORIZATION']
            # Kiểm tra xem header Authorization có chứa Bearer token không
            if auth_header.startswith('Bearer '):
                access_token = auth_header.split(' ')[1]
                # Thực hiện xác thực access_token ở đây
                # Nếu access_token hợp lệ, tiếp tục xử lý yêu cầu
                # Ví dụ: lấy đối tượng từ database và serialize nó
                user = User.objects.filter(active=True)
                serializer = serializers.UserSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
        # Nếu không có hoặc không hợp lệ, trả về lỗi 401 Unauthorized
        return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

