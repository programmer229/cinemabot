from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiohttp import ClientSession

Token = "1835667564:AAFFJCoUPoRjLGWWgx9iCjAoWqdv45QBvR4"
bot = Bot(token=Token)
dp = Dispatcher(bot)
api_key = "18d7a180e629c1d86830f4d5758821f5"


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я кинобот! Для справки напиши /help.")


@dp.message_handler(commands=['help'])
async def send_welcome(message: types.Message):
    await message.reply(
        "Справка для самых маленьких\nШаг 1) определяем что вам нужно сериал или фильм\nШаг 2) "
        "пишем сериал/фильм и далее название соотвествущего кино\nНапример \"фильм брат 2\"\n"
        "Шаг 3) радуемся:)")


@dp.message_handler()
async def main_handler(message: types.Message):
    text = message.text
    if len(text.split(' ')) == 1:
        await bot.send_message(text="Чел ты... Ошибочка вышла", chat_id=message.chat.id)
        return
    type_cinema, text = text.split(' ', 1)
    if type_cinema == "фильм":
        type_cinema = "movie"
    elif type_cinema == "сериал":
        type_cinema = "tv"
    else:
        await bot.send_message(text="Чел ты... Ошибочка вышла.", chat_id=message.chat.id)
        return
    parameters = [("api_key", api_key), ("language", "ru"), ("query", text)]
    async with ClientSession() as session:
        async with await session.get(url="https://api.themoviedb.org/3/search/" + type_cinema,
                                     params=parameters) as response:
            resp_json = await response.json()
            results = resp_json["results"]
            if len(results) == 0:
                await bot.send_message(text="Мда, попробуйте изменить название", chat_id=message.chat.id)
                return
            ans = {}
            best = 0
            for i in results:
                score = 0
                score += i["vote_average"]
                if type_cinema == "movie" and text.lower() in i["original_title"].lower():
                    score += 3
                if type_cinema == "movie" and text.lower() == i["original_title"].lower():
                    score += 3
                if type_cinema == "tv" and text.lower() in i["name"].lower():
                    score += 3
                if type_cinema == "tv" and text.lower() == i["name"].lower():
                    score += 3
                if score > best:
                    best = score
                    ans = i
            final_name = ""

            if type_cinema == "movie":
                await bot.send_message(text="Название кино: " + ans["original_title"], chat_id=message.chat.id)
                final_name = ans["original_title"]
            else:
                await bot.send_message(text="Название сериала: " + ans["name"], chat_id=message.chat.id)
                final_name = ans["name"]
            if len(ans["overview"]) > 0:
                await bot.send_message(text="Краткое описание: \n" + ans["overview"], chat_id=message.chat.id)
            final_name += " смотреть бесплатно"
            google_link = "https://google.com/search?q=" + final_name.replace(' ', "+")
            await bot.send_message(text=google_link, chat_id=message.chat.id)
            if ans["poster_path"] is not None:
                url = "http://image.tmdb.org/t/p/w600_and_h900_bestv2" + ans["poster_path"]
                async with session.get(url) as response:
                    await bot.send_photo(message.chat.id, await response.read())


if __name__ == '__main__':
    executor.start_polling(dp)
