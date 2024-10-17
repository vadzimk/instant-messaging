# instant-messaging app mvp

## Requirements specification
### User stories
- user wants to authenticate
- user wants to send and recieve messages
- user wants to see the message history
- user wants to receive notifications about new messages in telegram if user is offline
- user wants web-gui
### Technical stack requirements
- FastAPI
- PostgresSQL
- SqlAlchemy
- Celery (notifications queue)
- Redis (session storage)
- Docker
- Nginx
### Web GUI
- register
- login, logout
- send receive messages
- view message history