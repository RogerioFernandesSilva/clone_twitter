# Chirp — Clone do Twitter (Django REST + PostgreSQL)

Aplicação monolítica: API REST em **Django + Django REST Framework** (autenticação JWT) e front-end em HTML/CSS/JS puro servido pelo próprio Django (`/`).

## Funcionalidades
- Cadastro e login seguros (senha com hash + validadores do Django, JWT).
- Perfil: alterar **nome**, **foto** e **senha**, todos opcionais (PATCH parcial; trocar senha exige a senha atual).
- Seguir/deixar de seguir, listas de seguidores e seguidos.
- Feed apenas com postagens (e reposts) de quem você segue.
- CRUD de postagens (até 280 caracteres), curtidas, comentários e reposts.

## Rodando localmente
```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                              # opcional; sem DATABASE_URL usa SQLite
python manage.py migrate
python manage.py seed                             # 10 usuários fictícios (senha: Senha@12345)
python manage.py runserver
```
> **Windows/PowerShell:** rode cada comando em uma linha separada (o `&&` não funciona no PowerShell antigo; use `;` se quiser encadear). Para copiar o `.env`, use `copy .env.example .env`. **O `migrate` é obrigatório antes do primeiro uso**, senão aparece o erro `no such table: core_user`.
Acesse http://127.0.0.1:8000 e entre com, por exemplo, `ana_silva` / `Senha@12345`.

### PostgreSQL
Defina `DATABASE_URL=postgres://usuario:senha@host:5432/banco` antes de `migrate`.

## Dados fictícios (`python manage.py seed`)
10 usuários (`ana_silva`, `bruno_costa`, `carla_souza`, `diego_lima`, `elisa_rocha`, `fabio_alves`, `gabi_nunes`, `hugo_melo`, `isis_pires`, `joao_dias`), cada um com **3 tweets** e **2 reposts**, além de seguirem 3 outros usuários (para o feed já aparecer cheio). O comando é idempotente.

## Testes (56 testes, 8 por etapa)
```bash
python manage.py test
```
| Etapa | Arquivo |
|---|---|
| Autenticação | `core/tests/test_auth.py` |
| Perfil | `core/tests/test_profile.py` |
| Seguir | `core/tests/test_follow.py` |
| Feed | `core/tests/test_feed.py` |
| Postagens (CRUD) | `core/tests/test_posts.py` |
| Curtidas e comentários | `core/tests/test_interactions.py` |
| Reposts | `core/tests/test_reposts.py` |

## Endpoints (prefixo `/api`, header `Authorization: Bearer <access>`)
| Método | Rota | Descrição |
|---|---|---|
| POST | `/auth/register/` | Criar conta (`username`, `password`, `name`, `email` opc.) |
| POST | `/auth/login/` | Login → `access` e `refresh` |
| POST | `/auth/refresh/` | Renovar token |
| GET/PATCH | `/profile/` | Ver/editar perfil (`name`, `avatar`, `current_password`+`password`) |
| GET | `/users/?search=` | Listar usuários |
| GET | `/users/<username>/` | Detalhe do usuário |
| POST/DELETE | `/users/<username>/follow/` | Seguir / deixar de seguir |
| GET | `/users/<username>/followers/` · `/following/` | Seguidores / seguidos |
| GET | `/feed/` | Feed de quem eu sigo |
| GET/POST | `/posts/` | Listar (`?author=`) / criar |
| GET/PATCH/DELETE | `/posts/<id>/` | Ver / editar / apagar (só autor) |
| POST | `/posts/<id>/repost/` | Repostar |
| POST/DELETE | `/posts/<id>/like/` | Curtir / descurtir |
| GET/POST | `/posts/<id>/comments/` | Listar / comentar |
| DELETE | `/comments/<id>/` | Apagar comentário (só autor) |

> Fotos de perfil ficam no disco do servidor. Em planos gratuitos o disco é efêmero; para persistência use um disco persistente ou S3/Cloudinary.
