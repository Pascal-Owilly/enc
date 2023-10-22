from rest_framework import serializers
from .models import BlogPost, Like, Comment,Follower

class BlogPostSerializer(serializers.ModelSerializer):
    author_full_name = serializers.ReadOnlyField()

    class Meta:
        model = BlogPost
        fields = '__all__'

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follower
        fields = '__all__'