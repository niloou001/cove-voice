"""Ativacao local por voz. Audio permanece na memoria do computador."""
import ctypes
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import queue
import re
import subprocess
import sys
import time
import unicodedata

BASE = Path(__file__).resolve().parent

def is_wake_phrase(text):
    normalized = ''.join(c for c in unicodedata.normalize('NFD', text.lower()) if unicodedata.category(c) != 'Mn')
    words = re.findall(r'[a-z]+', normalized)
    # O nome Cove pode ser transcrito como "coube", "couve" ou "ouve".
    return bool(re.search(r'\b(?:oi|oie|ola) (?:cove|couve|coube|ouve|covi|cov) (?:o )?papai chegou\b', ' '.join(words)))

def launch():
    subprocess.Popen(['cmd.exe', '/c', str(BASE / 'Cove.bat')], creationflags=subprocess.CREATE_NO_WINDOW)

def main():
    import sounddevice as sd
    from vosk import Model, KaldiRecognizer, SetLogLevel
    handler = RotatingFileHandler(BASE / 'listener.log', maxBytes=200000, backupCount=2, encoding='utf-8')
    logging.basicConfig(level=logging.INFO, handlers=[handler], format='%(asctime)s %(levelname)s %(message)s')
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, 'Local\\CoveVoiceListener')
    if ctypes.windll.kernel32.GetLastError() == 183:
        return
    SetLogLevel(-1)
    model = Model(str(BASE / 'vosk-model-small-pt-0.3'))
    last_launch = 0
    while True:
        try:
            device = sd.query_devices(kind='input')
            rate = int(device['default_samplerate'])
            phrases = [f'{hello} {name} {article}papai chegou' for hello in ('oi', 'ola') for name in ('couve', 'coube', 'ouve') for article in ('', 'o ')]
            phrases += ['oi', 'ola', 'couve', 'coube', 'ouve', 'papai chegou', 'o papai chegou', '[unk]']
            recognizer = KaldiRecognizer(model, rate, json.dumps(phrases, ensure_ascii=False))
            recent = []
            last_status = time.monotonic()
            peak = 0
            audio = queue.Queue(maxsize=100)
            def callback(data, frames, timing, status):
                if not audio.full():
                    audio.put_nowait(bytes(data))
            with sd.RawInputStream(samplerate=rate, blocksize=4000, dtype='int16', channels=1, callback=callback):
                logging.info('Ouvindo no microfone: %s', device['name'])
                while True:
                    data = audio.get(timeout=15)
                    import array
                    peak = max(peak, max((abs(v) for v in array.array('h', data)), default=0))
                    final = recognizer.AcceptWaveform(data)
                    result = json.loads(recognizer.Result() if final else recognizer.PartialResult())
                    now = time.monotonic()
                    spoken = result.get('text', result.get('partial', ''))
                    recent = [(t, words) for t, words in recent if now - t < 8]
                    combined = ' '.join([words for t, words in recent] + [spoken])
                    if final and spoken:
                        recent.append((now, spoken))
                        if any(w in spoken.split() for w in ('oi', 'ola', 'papai', 'chegou')):
                            logging.info('Candidato de ativacao: %s', spoken)
                    if now - last_status > 60:
                        logging.info('Captura ativa; pico do microfone: %d/32768', peak)
                        last_status, peak = now, 0
                    if is_wake_phrase(combined) and now - last_launch > 20:
                        launch()
                        last_launch = time.monotonic()
                        logging.info('Frase de ativacao detectada; Cove aberto.')
                        recognizer.Reset()
                        recent.clear()
        except Exception:
            logging.exception('Falha de audio; nova tentativa em 10 segundos')
            time.sleep(10)

if __name__ == '__main__':
    if '--test' in sys.argv:
        assert is_wake_phrase('Oi Cove, papai chegou')
        assert is_wake_phrase('oi couve o papai chegou')
        assert not is_wake_phrase('papai chegou')
        assert not is_wake_phrase('oi cove tudo bem')
        print('Frases de ativacao verificadas.')
    elif '--launch-test' in sys.argv:
        launch()
    else:
        main()
