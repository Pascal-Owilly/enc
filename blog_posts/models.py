from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class BlogPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='blog_post_images/', blank=True, null=True)

    def __str__(self):
        return f'{self.content} by {self.author}'

    def author_full_name(self):
        if self.author.first_name and self.author.last_name:
            return f"{self.author.first_name} {self.author.last_name}"
        else:
            return self.author.username

    def author_current_city(self):
        return self.author.profile.current_city if hasattr(self.author, 'profile') else None

    def __str__(self):
        return f"{self.content} - {self.created_at.strftime('%d %b %Y')}"

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} likes {self.post.author}'s post "

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} commented {self.post.author}'s post "

class Follower(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')

    def __str__(self):
        return f"{self.user} follows {self.follower} "