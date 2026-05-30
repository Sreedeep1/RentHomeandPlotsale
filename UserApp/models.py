from django.db import models
from homeapp.models import tbl_user
from django.db.models import Q
from adminapp.models import tbl_category
# Create your models here.
class tbl_property(models.Model):

    FURNISHING_CHOICES = [
        ('Furnished', 'Furnished'),
        ('Semi-Furnished', 'Semi-Furnished'),
        ('Unfurnished', 'Unfurnished'),
    ]

    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Occupied', 'Occupied'),
        ('Maintenance', 'Maintenance'),
    ]

    owner = models.ForeignKey(
        tbl_user,
        on_delete=models.CASCADE,
        related_name='properties'
    )

    title = models.CharField(max_length=200)
    description = models.TextField()

    # ✅ NEW FIELDS
    address = models.CharField(max_length=255)
   
    location = models.CharField(max_length=255)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)

    home_type = models.ForeignKey(tbl_category, on_delete=models.CASCADE)

    furnishing = models.CharField(max_length=20, choices=FURNISHING_CHOICES)

    bedrooms = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField()
    size_sqft = models.PositiveIntegerField()

    availability_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Available'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.address}"
    @property
    def chat_messages_count(self):
        """Get count of unread messages for this property's chat rooms"""
        from django.db.models import Q, Count
        
        # Get all chat rooms for this property
        chat_rooms = tbl_chat_room.objects.filter(property=self)
        
        # Count unread messages where current user is not the sender
        # You'll need to pass the current user - this is a placeholder
        # Better to handle this in the view
        return 0  # Placeholder
    
    def get_unread_count_for_user(self, user):
        """Get unread message count for a specific user"""
        chat_rooms = tbl_chat_room.objects.filter(
            Q(property=self) & 
            (Q(user1=user) | Q(user2=user))
        )
        
        total_unread = 0
        for room in chat_rooms:
            unread = room.messages.filter(
                ~Q(sender=user),  # Not sent by current user
                is_read=False
            ).count()
            total_unread += unread
        
        return total_unread
    
class tbl_property_images(models.Model):

    property = models.ForeignKey(
        tbl_property,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = models.ImageField(upload_to='property_images/')

    def __str__(self):
        return f"Image for {self.property.title}"



class tbl_plot_for_sale(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Sold', 'Sold'),
        ('Reserved', 'Reserved'),
    ]
    PLOT_TYPE_CHOICES = [
    ('Purayidam', 'Purayidam (Residential)'),
    ('Residential', 'Residential Plot'),
    ('Parambu', 'Parambu (Dry Land)'),
    ('Thottam', 'Thottam (Plantation)'),
    ('Vayal', 'Vayal (Paddy Land)'),
    ('Nilam', 'Nilam (Wet Land)'),
    ('Commercial', 'Commercial Plot'),
    ('Mixed', 'Mixed Use'),
]

    owner = models.ForeignKey(tbl_user, on_delete=models.CASCADE, related_name='plots')

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    # Essential details
    address = models.CharField(max_length=255)
    area = models.PositiveIntegerField(help_text="Area in sq ft or sq meters")
    price = models.DecimalField(max_digits=12, decimal_places=2)

    # Optional categorization
    
    plot_type = models.CharField(
        max_length=30,
        choices=PLOT_TYPE_CHOICES,
        default='Purayidam'
    )
    # Utilities / Features (optional)
    water = models.BooleanField(default=False)
    electricity = models.BooleanField(default=False)
    gated_community = models.BooleanField(default=False)

    availability_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Available'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.address}"
    def first_image(self):
        """Get the first image for the plot"""
        return self.images.first()
class tbl_plot_images(models.Model):
    plot = models.ForeignKey(tbl_plot_for_sale, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='plot_images/')

    def __str__(self):
        return f"Image for {self.plot.title}"

############chat model##########

class tbl_chat_room(models.Model):
    user1 = models.ForeignKey(tbl_user, on_delete=models.CASCADE, related_name='chat_user1')
    user2 = models.ForeignKey(tbl_user, on_delete=models.CASCADE, related_name='chat_user2')
    
    property = models.ForeignKey(tbl_property, on_delete=models.CASCADE, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user1} - {self.user2}"
    class Meta:
        unique_together = ('user1', 'user2', 'property')  # 🔥 prevents duplicate rooms
class tbl_chat_message(models.Model):
    chat_room = models.ForeignKey(tbl_chat_room, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(tbl_user, on_delete=models.CASCADE)
    
    message = models.TextField()
    
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} - {self.timestamp}"
    

class tbl_plot_interest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('contacted', 'Contacted'),
        ('rejected', 'Rejected'),
    ]
    plot = models.ForeignKey(tbl_plot_for_sale, on_delete=models.CASCADE)
    user = models.ForeignKey(tbl_user, on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    response_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('plot', 'user')   # prevent duplicate interest


class tbl_plot_wishlist(models.Model):
    plot = models.ForeignKey(tbl_plot_for_sale, on_delete=models.CASCADE)
    user = models.ForeignKey(tbl_user, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('plot', 'user')   # prevent duplicate wishlist

# ... existing models ...

class tbl_feedback(models.Model):

    FEEDBACK_TYPE_CHOICES = [
        ('complaint', 'Complaint'),
        ('suggestion', 'Suggestion'),
        ('bug', 'Bug Report'),
        ('feature', 'Feature Request'),
        ('technical', 'Technical Issue'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(
        tbl_user,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    subject = models.CharField(max_length=200)
    message = models.TextField()
    feedback_type = models.CharField(
        max_length=20,
        choices=FEEDBACK_TYPE_CHOICES,
        default='other'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.subject}"

    class Meta:
        ordering = ['-created_at']