from django.db import models


class Song(models.Model):
    title = models.CharField(max_length=255, blank=False)
    artist = models.CharField(max_length=255, blank=True, null=True)
    length = models.TimeField(blank=True, null=True)
    speed = models.IntegerField(blank=True, null=True)
    speed.help_text = 'The speed of the song in TPM'
    style = models.ForeignKey('Style', related_name='songs', blank=False, null=True, on_delete=models.SET_NULL)
    url_video = models.URLField(max_length=500, blank=True, null=True)
    url_video.help_text = 'A url to a demo video (e.g Youtube).'

    def __str__(self):
        return '{} - {}'.format(self.title, self.artist)

    class Meta:
        ordering = ['speed', 'length']
