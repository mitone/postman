import settings


if settings.USE_MEMORY_STORAGE:
    from aiogram.contrib.fsm_storage.memory import MemoryStorage
    aio_storage = MemoryStorage()
else:
    from aiogram.contrib.fsm_storage.redis import RedisStorage2
    aio_storage = RedisStorage2(settings.REDIS_HOST, settings.REDIS_PORT, db=2,
                        pool_size=3, prefix='postman_fsm')
