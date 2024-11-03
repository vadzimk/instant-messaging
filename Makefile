demo.up:
	docker-compose \
	-f docker-compose.demo.yml \
	-p messaging-demo up -d

demo.down:
	docker-compose -p messaging-demo down

demo.clean:
	docker-compose \
	-f docker-compose.demo.yml \
	-p messaging-demo down --volumes --remove-orphans