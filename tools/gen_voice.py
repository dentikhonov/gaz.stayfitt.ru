"""Генерирует озвучку фраз в voice/*.mp3 и voice/voice.json (текст из облачка -> файл).

Запуск: pip install edge-tts && python3 tools/gen_voice.py   (нужен ffmpeg)
Каваи-фразы читает ru-RU-SvetlanaNeural с поднятым тоном, мужские — ja-JP-KeitaNeural
по катакане, чтобы русский звучал с японским акцентом.
"""
import asyncio, json, os, subprocess, tempfile

import edge_tts

KAWAII = dict(voice="ru-RU-SvetlanaNeural", pitch="+45Hz", rate="+8%")
SENPAI = dict(voice="ja-JP-KeitaNeural", pitch="-4Hz", rate="+5%")
SHOUT = dict(voice="ja-JP-KeitaNeural", pitch="+6Hz", rate="+12%", volume="+20%")

# (текст в облачке на странице, что произносим, голос)
LINES = [
    ("Охаёшечки!", "Охаёшечки!", KAWAII),
    ("Датебаёшечки!", "ダッテバヨーシェチキ！", SENPAI),
    ("Аригатошечки~", "Аригато-шечки!", KAWAII),
    ("Ня~", "Ня-а!", KAWAII),
    ("Мур-мур-мур…", "Мур-мур-мур…", KAWAII),
    ("Каваи десу нэ~", "Кава-и десу нэ!", KAWAII),
    ("Сугоооой!", "すごーーーい！", SENPAI),
    ("Ара-ара~", "Ара-ара…", KAWAII),
    ("Нани?!", "なにっ？！", SHOUT),
    ("Омаэ ва моу… уволен. Шучу, ня!", "お前はもう…ウヴォーリェン。シュチュー、ニャ！", SENPAI),
    ("Сэмпай заметил тебя!", "Сэмпай заметил тебя!", KAWAII),
    ("Уву~", "Уву!", KAWAII),
    ("Газуем, ня!", "ガズイェム、ニャ！", SHOUT),
    ("Ути-пути, синергия~", "Ути-пути, синергия!", KAWAII),
    ("Ямэро, щекотно!", "Ямэро, щекотно!", KAWAII),
    ("Ичи, ни, сан… ГАЗ!", "いち、に、さん…ガズ！", SHOUT),
    ("Пасибки-шмасибки!", "Пасибки-шмасибки!", KAWAII),
    ("Йоу, ребятки, стендап через пять минуточек~", "Йоу, ребятки, стендап через пять минуточек!", KAWAII),
    ("Кавайный квартал, ня!", "Кавайный квартал, ня!", KAWAII),
    ("Бака! Кто деплоит в пятницу?!", "Бака! Кто деплоит в пятницу?!", KAWAII),
    ("Моя сила уровня больше девяти тысяч!", "マヤ・シーラ・ウローヴニャ、ボーリシェ・デヴャーチ・ティーシャチ！", SHOUT),
    ("Ня-ня, одобряю бюджет~", "Ня-ня, одобряю бюджет!", KAWAII),
    ("Мимими, какой ты молодец!", "Ми-ми-ми, какой ты молодец!", KAWAII),
    ("Ещё! Ещё гладь!", "Ещё! Ещё гладь!", KAWAII),
    ("ГАЗ!", "ガズ！", SHOUT),
    ("ГАЗ! ГАЗ! ГАЗ!", "ガズ！ガズ！ガズ！", SHOUT),
    ("Газ-газ-газ, сэмпай!", "ガズ、ガズ、ガズ、センパイ！", SHOUT),
    ("ГАЗУЕЕЕМ!", "ガズイェーーーム！", SHOUT),
]

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "voice")


async def main():
    os.makedirs(ROOT, exist_ok=True)
    manifest = {}
    with tempfile.TemporaryDirectory() as tmp:
        for i, (key, spoken, opts) in enumerate(LINES, 1):
            name = f"v{i:02d}.mp3"
            raw = os.path.join(tmp, name)
            await edge_tts.Communicate(spoken, **opts).save(raw)
            # срезаем тишину в начале и выравниваем громкость обоих голосов
            subprocess.run([
                "ffmpeg", "-loglevel", "error", "-y", "-i", raw,
                "-af", "silenceremove=start_periods=1:start_threshold=-50dB,loudnorm=I=-15:TP=-1.5",
                "-ar", "24000", "-ac", "1", "-b:a", "64k", os.path.join(ROOT, name),
            ], check=True)
            manifest[key] = name
            print(name, key)
    with open(os.path.join(ROOT, "voice.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)


asyncio.run(main())
