from aiohttp import web

from src.logger import logger


async def notification_handler(request: web.Request):
    try:
        bot = request.app['bot']

        data = await request.json()
        tg_user_id = data.get('tg_user_id')
        content = data.get('content')
        if not tg_user_id or not content:
            return web.json_response({'error': 'tg_user_id and content are required'}, status=400)

        # send message to the specified user
        await bot.send_message(chat_id=tg_user_id, text=content)
        return web.json_response(status=204)
    except Exception as exc:
        logger.error('Failed to send message: ', str(exc))
        return web.json_response({'error': "Failed to send message"}, status=500)


async def webhook_handler(request: web.Request):
    """ Handle incoming updates from Telegram """
    bot = request.app['bot']
    dp = request.app['dp']

    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return web.Response(text='OK')
