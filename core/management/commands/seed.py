from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.models import Post

User = get_user_model()
PASSWORD = "Senha@12345"

DATA = [
    ("ana_silva", "Ana Silva", "café"), ("bruno_costa", "Bruno Costa", "futebol"),
    ("carla_souza", "Carla Souza", "música"), ("diego_lima", "Diego Lima", "programação"),
    ("elisa_rocha", "Elisa Rocha", "viagens"), ("fabio_alves", "Fábio Alves", "cinema"),
    ("gabi_nunes", "Gabriela Nunes", "livros"), ("hugo_melo", "Hugo Melo", "games"),
    ("isis_pires", "Ísis Pires", "culinária"), ("joao_dias", "João Dias", "ciclismo"),
]
TEMPLATES = [
    "Bom dia, pessoal! Hoje o assunto é {topic}.",
    "Alguém mais aqui é apaixonado por {topic}? Me contem suas dicas!",
    "Fim de semana dedicado a {topic}. Recomendo demais.",
]


class Command(BaseCommand):
    help = "Cria 10 usuários fictícios, cada um com 3 tweets e 2 reposts (senha: Senha@12345)."

    def handle(self, *args, **opts):
        users = []
        for username, name, topic in DATA:
            u, created = User.objects.get_or_create(
                username=username, defaults={"first_name": name, "email": f"{username}@exemplo.com"})
            if created:
                u.set_password(PASSWORD)
                u.save()
                for t in TEMPLATES:
                    Post.objects.create(author=u, content=t.format(topic=topic))
            users.append(u)

        n = len(users)
        for i, u in enumerate(users):
            u.following.add(*[users[(i + k) % n] for k in (1, 2, 3)])
            for k in (1, 2):  # 2 reposts por usuário, de tweets de outras pessoas
                originals = list(users[(i + k) % n].posts.filter(repost_of__isnull=True).order_by("id"))
                if len(originals) >= k:
                    Post.objects.get_or_create(author=u, repost_of=originals[k - 1])

        self.stdout.write(self.style.SUCCESS(
            f"Seed ok: {User.objects.count()} usuários, {Post.objects.filter(repost_of__isnull=True).count()} tweets, "
            f"{Post.objects.filter(repost_of__isnull=False).count()} reposts."))
