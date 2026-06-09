from .models import Bildirishnoma


def bildir(user, matn, havola='', turi='info'):
    """Foydalanuvchiga bildirishnoma yaratadi."""
    if user is None:
        return None
    return Bildirishnoma.objects.create(
        foydalanuvchi=user, matn=matn, havola=havola, turi=turi
    )
