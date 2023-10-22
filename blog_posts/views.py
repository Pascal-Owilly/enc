from rest_framework import viewsets, status, serializers, permissions, filters
from .models import BlogPost, Like, Comment, Follower
from .serializers import BlogPostSerializer, LikeSerializer, CommentSerializer, FollowerSerializer
from rest_framework.response import Response
from django.db.models import Q  # Import Q for complex lookups
from rest_framework.decorators import action  # Import the action decorator
from rest_framework.permissions import IsAuthenticated
from blog_posts.permissions import isAuthorOrReadOnly

import logging

logger = logging.getLogger(__name__)


class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all().order_by('-created_at')
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticated, isAuthorOrReadOnly]  # Add IsAuthenticated permission
    filter_backends = [filters.SearchFilter]
    search_fields = ['author__user__icontains', 'content__icontains']
    

     # Add a custom search action
    @action(detail=False, methods=['GET'])
    def search(self, request):
        query = request.query_params.get('query', '')

        # Perform a search across multiple fields and models using Q objects
        results = BlogPost.objects.filter(
            Q(author__icontains=query) | Q(content__icontains=query)
        ).order_by('-created_at')

        serializer = BlogPostSerializer(results, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Try to save the serializer and create the blog post
            serializer.save(author=request.user)

            # Initialize comments and likes for the newly created blog post
            blog_post = serializer.instance
            blog_post.comments = []  # Initialize with an empty list of comments
            blog_post.likes = 0  # Initialize with 0 likes
            blog_post.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except serializers.ValidationError as e:
            # Handle the validation error and print detailed error messages
            for field, errors in e.detail.items():
                for error_message in errors:
                    print(f"Validation Error for field '{field}': {error_message}")
            return Response({'errors': 'Validation errors occurred'}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as ex:
            # Handle other exceptions and print the error message
            error_message = str(ex)
            print(f"Unexpected Exception: {error_message}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all().order_by('-id')
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            # Check if the user has already liked the post
            post_id = request.data.get('post')
            user = request.user  # Get the authenticated user

            existing_like = Like.objects.filter(post_id=post_id, user=user).first()

            if existing_like:
                # If the user has already liked the post, return a conflict response
                return Response({'detail': 'You have already liked this post.'}, status=status.HTTP_409_CONFLICT)

            # Automatically associate the like with the authenticated user
            like_data = {'post': post_id, 'user': user.pk}
            serializer = self.get_serializer(data=like_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
        except Exception as ex:
            # Log the exception for debugging purposes
            logger.exception("Error while creating a like:")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-id')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            # Extract post ID and comment text from request data
            post_id = request.data.get('post')
            text = request.data.get('text')
            user = request.user  # Get the authenticated user

            # Create a new comment and associate it with the authenticated user
            comment_data = {'post': post_id, 'user': user.pk, 'text': text}
            serializer = self.get_serializer(data=comment_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as ex:
            # Log the exception for debugging purposes
            logger.exception("Error while creating a comment:")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FollowerViewSet(viewsets.ModelViewSet):
    queryset = Follower.objects.all().order_by('-id')
    serializer_class = FollowerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            # Extract user to follow from request data
            user_to_follow_id = request.data.get('user_to_follow')
            user = request.user  # Get the authenticated user

            # Create a new follower association and associate it with the authenticated user
            follower_data = {'user': user.pk, 'user_to_follow': user_to_follow_id}
            serializer = self.get_serializer(data=follower_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as ex:
            # Log the exception for debugging purposes
            logger.exception("Error while creating a follower association:")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
