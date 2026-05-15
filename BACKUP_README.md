## CodefortifyAuth Backup and Restore

## 1) PostgreSQL Backup (Docker)

Create SQL dump from running `db` service:

```bash
docker compose exec -T db pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" > backup_$(date +%Y%m%d_%H%M%S).sql
```

For production compose:

```bash
docker compose -f docker-compose.prod.yml exec -T db pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" > backup_prod_$(date +%Y%m%d_%H%M%S).sql
```

---

## 2) PostgreSQL Restore (Docker)

Restore from a dump file:

```bash
cat backup_file.sql | docker compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

Production compose:

```bash
cat backup_file.sql | docker compose -f docker-compose.prod.yml exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

After restore:

```bash
docker compose exec web python manage.py migrate
```

---

## 3) Docker Volume Backup Notes

List volumes:

```bash
docker volume ls | grep codefortifyauth
```

Main persistent volumes:

- PostgreSQL: `postgres_data`
- Redis: `redis_data`
- Media: `media_data`

You can archive volumes with a temporary container, but SQL dump + media backup is usually enough for app recovery.

---

## 4) Media Backup

Create media archive:

```bash
docker run --rm \
  -v codefortifyauth_media_data:/data \
  -v "$(pwd)":/backup \
  alpine \
  tar czf /backup/media_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .
```

Restore media archive:

```bash
docker run --rm \
  -v codefortifyauth_media_data:/data \
  -v "$(pwd)":/backup \
  alpine \
  sh -c "tar xzf /backup/media_backup.tar.gz -C /data"
```

Adjust volume name if your Compose project name differs.

---

## 5) SQLite Backup (Non-Docker Local)

If using local SQLite fallback (`DATABASE_URL` empty):

```bash
cp db.sqlite3 db.sqlite3.backup_$(date +%Y%m%d_%H%M%S)
```

SQLite restore:

```bash
cp db.sqlite3.backup_YYYYMMDD_HHMMSS db.sqlite3
```
