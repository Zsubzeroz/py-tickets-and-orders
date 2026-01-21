from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.conf import settings


class User(AbstractUser):
    pass


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        indexes = [
            models.Index(fields=["title"]),
        ]


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


class Ticket(models.Model):
    movie_session = models.ForeignKey(
        "MovieSession", on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )
    row = models.IntegerField()
    seat = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["movie_session", "row", "seat"],
                name="unique_ticket_session"
            )
        ]

    def clean(self) -> None:
        # Validate row
        if not (1 <= self.row <= self.movie_session.cinema_hall.rows):
            raise ValidationError({
                "row": [f"row number must be in available range: (1, rows): (1, {self.movie_session.cinema_hall.rows})"]
            })

        # Validate seat
        if not (1 <= self.seat <= self.movie_session.cinema_hall.seats_in_row):
            raise ValidationError({
                "seat": [
                    f"seat number must be in available range: (1, seats_in_row): (1, {self.movie_session.cinema_hall.seats_in_row})"]
            })

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (f"{self.movie_session.movie.title} "
                f"{self.movie_session.show_time.strftime('%Y-%m-%d %H:%M:%S')} "
                f"(row: {self.row}, seat: {self.seat})")
