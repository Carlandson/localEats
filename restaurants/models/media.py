from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from PIL import Image as PILImage
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
import logging
import magic

logger = logging.getLogger(__name__)
User = get_user_model()


class Image(models.Model):
    image = models.ImageField(upload_to='user_uploads/%Y/%m/%d/')
    thumbnail = models.ImageField(upload_to='thumbnails/%Y/%m/%d/', blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_images')
    upload_date = models.DateTimeField(auto_now_add=True)
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    alt_text = models.CharField(max_length=255, blank=True)
    caption = models.TextField(blank=True)

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_FILE_SIZE = 10 * 1024 * 1024 # 10MB
    VALID_CONTENT_TYPES = {
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp'
    }

    def clean(self):
        if self.image:
            original_position = self.image.tell()
            
            try:
                # Content type check
                self.image.seek(0)
                content_type = magic.from_buffer(self.image.read(1024), mime=True)
                logger.debug(f"Content type check: {content_type}")
                if content_type not in self.VALID_CONTENT_TYPES:
                    raise ValidationError(f'Unsupported content type: {content_type}')
                
                # File size check
                self.image.seek(0)
                if self.image.size > self.MAX_FILE_SIZE:
                    raise ValidationError('File size cannot exceed 10MB.')
                
                # Extension check
                ext = self.image.name.split('.')[-1].lower()
                if ext not in self.ALLOWED_EXTENSIONS:
                    raise ValidationError(f'Unsupported file extension. Allowed types: {", ".join(self.ALLOWED_EXTENSIONS)}')
                
                # Image verification
                self.image.seek(0)
                try:
                    img = PILImage.open(self.image)
                    # Don't use verify() as it can be problematic
                    # Instead, try to load the image
                    img.load()
                except Exception as e:
                    logger.error(f"PIL Image verification failed: {str(e)}")
                    raise ValidationError(f'Invalid image file: {str(e)}')
                    
            except ValidationError:
                raise
            except Exception as e:
                logger.error(f"Unexpected error in image validation: {str(e)}")
                raise ValidationError(f'Error processing image: {str(e)}')
            finally:
                self.image.seek(original_position)
            
    def save(self, *args, **kwargs):
        logger.debug(f"""
            Saving Image:
            - Alt Text: {self.alt_text}
            - Content Type: {self.content_type}
            - Object ID: {self.object_id}
            - Content Object: {self.content_object}
            - Image Path: {self.image.name if self.image else 'No image'}
        """)
        if not self.id:
            self.full_clean()
            self.image = self.compress_image(self.image)
            self.create_thumbnail()
        super(Image, self).save(*args, **kwargs)
        logger.debug(f"""
            Image Saved:
            - ID: {self.id}
            - Alt Text: {self.alt_text}
            - Content Type: {self.content_type}
            - Object ID: {self.object_id}
        """)

    def compress_image(self, uploadedImage):
        try:
            im = PILImage.open(uploadedImage)
            #verify image format
            if im.format.upper() not in ['PNG', 'JPEG', 'GIF', 'WEBP']:
                raise ValidationError('Unsupported image format')
        
            # Convert to RGB if necessary
            if im.mode != 'RGB':
                im = im.convert('RGB')
            
            # Resize if larger than 1920x1080
            if im.width > 1920 or im.height > 1080:
                output_size = (1920, 1080)
                im.thumbnail(output_size)
            
            # Convert to WebP
            im_io = BytesIO()
            im.save(im_io, 'WEBP', quality=70, optimize=True)
            new_image = InMemoryUploadedFile(im_io, 'ImageField', "%s.webp" % uploadedImage.name.split('.')[0], 'image/webp', sys.getsizeof(im_io), None)
            return new_image
        
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            raise ValidationError('Error processing image file')

    def create_thumbnail(self):
        if not self.image:
            return
        
        im = PILImage.open(self.image)
        im.thumbnail((100, 100))
        thumb_io = BytesIO()
        im.save(thumb_io, 'WEBP', quality=60)
        thumbnail = InMemoryUploadedFile(thumb_io, 'ImageField', "%s_thumb.webp" % self.image.name.split('.')[0], 'image/webp', sys.getsizeof(thumb_io), None)
        self.thumbnail.save("%s_thumb.webp" % self.image.name.split('.')[0], thumbnail, save=False)

    def __str__(self):
        return f"Image for {self.content_object} - {self.upload_date}"