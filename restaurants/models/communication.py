from django.db import models
from django.contrib.auth import get_user_model
from .content import NewsFeed

User = get_user_model()

class ContactMessage(models.Model):
    business = models.ForeignKey('Business', on_delete=models.CASCADE, related_name='contact_messages')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.name} to {self.business.business_name}"
    
class NewsPost(models.Model):
    news_feed = models.ForeignKey(NewsFeed, on_delete=models.CASCADE, related_name='news_posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, blank=True, related_name="user_liked")

class Comment(models.Model):
    news_post = models.ForeignKey(NewsPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)