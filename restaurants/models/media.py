import sys
import logging
import magic
import hashlib

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile

from PIL import Image as PILImage
from io import BytesIO

logger = logging.getLogger(__name__)
User = get_user_model()


class Image(models.Model):
    image = models.ImageField(upload_to='user_uploads/%Y/%m/%d/')
    thumbnail = models.ImageField(upload_to='thumbnails/%Y/%m/%d/', blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_images')
    upload_date = models.DateTimeField(auto_now_add=True)

    #hash
    file_hash = models.CharField(max_length=32, unique=True, db_index=True, blank=True, null=True)

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

    def save(self, *args, **kwargs):
        check_duplicate = kwargs.pop('check_duplicate', True)
        allow_duplicate_in_different_location = kwargs.pop('allow_duplicate_in_different_location', False)
        
        logger.debug(f"""
            Saving Image:
            - Alt Text: {self.alt_text}
            - Content Type: {self.content_type}
            - Object ID: {self.object_id}
            - Check Duplicate: {check_duplicate}
        """)
        
        if not self.id:
            self.full_clean()
            self.image = self.compress_image(self.image)
            self.file_hash = self._calculate_hash(self.image)
            # Check for duplicate if enabled
            if check_duplicate and self.file_hash:
                existing_image = Image.objects.filter(
                    file_hash=self.file_hash
                ).exclude(id=self.id if self.id else None).first()
                
                if existing_image:
                    # Check if it's in the same location
                    is_same_location = (
                        existing_image.content_type == self.content_type and
                        existing_image.object_id == self.object_id
                    )
                    
                    if is_same_location:
                        # Duplicate in same location - raise error
                        raise ValidationError(
                            f'This image already exists in this location. '
                            f'Existing image ID: {existing_image.id}'
                        )
                    elif not allow_duplicate_in_different_location:
                        # Duplicate in different location - optionally raise error
                        raise ValidationError(
                            f'This image already exists elsewhere. '
                            f'Existing image ID: {existing_image.id}'
                        )
                    # If allow_duplicate_in_different_location is True, we allow it
            
            self.create_thumbnail()

        
        super(Image, self).save(*args, **kwargs)
        logger.debug(f"Image Saved - ID: {self.id}")

    @staticmethod
    def _calculate_hash(file):
        """Calculate MD5 hash of file content."""
        file.seek(0)
        hash_md5 = hashlib.md5()
        for chunk in file.chunks():
            hash_md5.update(chunk)
        file.seek(0)
        return hash_md5.hexdigest()

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

    def compress_image(self, uploadedImage):
        try:
            logger.debug(f"Compressing image: {uploadedImage.name}")
            uploadedImage.seek(0)
            im = PILImage.open(uploadedImage)
            #verify image format
            if im.format and im.format.upper() == 'MPO':
                # MPO is JPEG-based, so we can process it
                # If it's a multi-frame image, PIL will use the first frame
                logger.debug(f"Processing MPO format image, using first frame")
            elif not im.format or im.format.upper() not in ['PNG', 'JPEG', 'GIF', 'WEBP']:
                logger.error(f"Unsupported image format: {im.format}")
                raise ValidationError(f'Unsupported image format: {im.format or "Unknown"}')
        
        
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
            im_io.seek(0)
            new_image = InMemoryUploadedFile(im_io, 'ImageField', "%s.webp" % uploadedImage.name.split('.')[0], 'image/webp', sys.getsizeof(im_io), None)
            return new_image
        except ValidationError:
            raise
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