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

### TODO
    # frontend
        # ui to send messages and see history
    # backend
        # when user connects, his status becomes online
            # when user disconnects, his status becomes offline, and last_active_at timestamp is saved in db
            # you can query redis for sio to see who is online
        # chatbot and celery notification queue when offline
            # add telegram username to user model
    # devops
        # make app docker image
        # make nginx reverse-proxy service