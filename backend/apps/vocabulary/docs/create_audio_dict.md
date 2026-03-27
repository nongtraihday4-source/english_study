# Tạo audio cho tất cả từ (mặc định voice en-GB-SoniaNeural)
python manage.py generate_tts_audio

# Chỉ tạo 500 từ đầu (sorted by frequency_rank)
python manage.py generate_tts_audio --limit 500

# Force tái tạo dù đã có cache
python manage.py generate_tts_audio --force