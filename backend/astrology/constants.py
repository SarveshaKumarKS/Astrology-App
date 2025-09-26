# Astrological Constants for Tamil Astrology

# Planets
PLANETS = {
    1: 'Sun', 2: 'Moon', 3: 'Mars', 4: 'Mercury', 5: 'Jupiter',
    6: 'Venus', 7: 'Saturn', 8: 'Rahu', 9: 'Ketu'
}

PLANETS_TAMIL = {
    1: 'சூரியன்', 2: 'சந்திரன்', 3: 'செவ்வாய்', 4: 'புதன்', 5: 'குரு',
    6: 'சுக்ரன்', 7: 'சனி', 8: 'ராகு', 9: 'கேது'
}

PLANET_NAMES = {
    'Sun': 'சூரியன்', 'Moon': 'சந்திரன்', 'Mars': 'செவ்வாய்', 'Mercury': 'புதன்', 
    'Jupiter': 'குரு', 'Venus': 'சுக்ரன்', 'Saturn': 'சனி', 'Rahu': 'ராகு', 'Ketu': 'கேது'
}

# Zodiac Signs (Rasi)
SIGNS = {
    1: 'Aries', 2: 'Taurus', 3: 'Gemini', 4: 'Cancer', 5: 'Leo', 6: 'Virgo',
    7: 'Libra', 8: 'Scorpio', 9: 'Sagittarius', 10: 'Capricorn', 11: 'Aquarius', 12: 'Pisces'
}

SIGNS_TAMIL = {
    1: 'மேஷம்', 2: 'ரிஷபம்', 3: 'மிதுனம்', 4: 'கடகம்', 5: 'சிம்மம்', 6: 'கன்னி',
    7: 'துலாம்', 8: 'விருச்சிகம்', 9: 'தனுசு', 10: 'மகரம்', 11: 'கும்பம்', 12: 'மீனம்'
}

# Nakshatras (Stars)
NAKSHATRAS = {
    1: 'Ashwini', 2: 'Bharani', 3: 'Krittika', 4: 'Rohini', 5: 'Mrigashira',
    6: 'Ardra', 7: 'Punarvasu', 8: 'Pushya', 9: 'Ashlesha', 10: 'Magha',
    11: 'Purva Phalguni', 12: 'Uttara Phalguni', 13: 'Hasta', 14: 'Chitra', 15: 'Swati',
    16: 'Vishakha', 17: 'Anuradha', 18: 'Jyeshtha', 19: 'Mula', 20: 'Purva Ashadha',
    21: 'Uttara Ashadha', 22: 'Shravana', 23: 'Dhanishta', 24: 'Shatabhisha', 25: 'Purva Bhadrapada',
    26: 'Uttara Bhadrapada', 27: 'Revati'
}

NAKSHATRAS_TAMIL = {
    1: 'அஸ்வினி', 2: 'பரணி', 3: 'கிருத்திகை', 4: 'ரோஹிணி', 5: 'மிருகசீர்ஷம்',
    6: 'திருவாதிரை', 7: 'புனர்பூசம்', 8: 'பூசம்', 9: 'ஆயில்யம்', 10: 'மகம்',
    11: 'பூரம்', 12: 'உத்திரபல்குனி', 13: 'ஹஸ்தம்', 14: 'சித்திரை', 15: 'ஸ்வாதி',
    16: 'விசாகம்', 17: 'அனுஷம்', 18: 'கேட்டை', 19: 'மூலம்', 20: 'பூராடம்',
    21: 'உத்திராடம்', 22: 'திருவோணம்', 23: 'அவிட்டம்', 24: 'சதயம்', 25: 'பூரட்டாதி',
    26: 'உத்திரட்டாதி', 27: 'ரேவதி'
}

# Houses (Bhava)
HOUSES = {
    1: 'Lagna', 2: 'Dhana', 3: 'Sahaja', 4: 'Sukha', 5: 'Putra', 6: 'Shatru',
    7: 'Kalatra', 8: 'Ayus', 9: 'Bhagya', 10: 'Karma', 11: 'Labha', 12: 'Vyaya'
}

HOUSES_TAMIL = {
    1: 'லக்னம்', 2: 'தனம்', 3: 'சகோதரம்', 4: 'சுகம்', 5: 'புத்திரம்', 6: 'சத்ரு',
    7: 'கலத்திரம்', 8: 'ஆயுள்', 9: 'பாக்கியம்', 10: 'கர்மம்', 11: 'லாபம்', 12: 'வியாயம்'
}

# Dasa Order (Vimshottari)
DASA_ORDER = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
DASA_YEARS = {
    'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
    'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
}

# Compatibility Factors (Ashtakoota)
COMPATIBILITY_FACTORS = {
    'varna': {'name': 'Varna', 'tamil': 'வர்ணம்', 'max_points': 1},
    'vashya': {'name': 'Vashya', 'tamil': 'வஷ்யம்', 'max_points': 2},
    'tara': {'name': 'Tara', 'tamil': 'தாரம்', 'max_points': 3},
    'yoni': {'name': 'Yoni', 'tamil': 'யோனி', 'max_points': 4},
    'graha_maitri': {'name': 'Graha Maitri', 'tamil': 'கிரக மைத்ரி', 'max_points': 5},
    'gana': {'name': 'Gana', 'tamil': 'கணம்', 'max_points': 6},
    'bhakoot': {'name': 'Bhakoot', 'tamil': 'பகூத்', 'max_points': 7},
    'nadi': {'name': 'Nadi', 'tamil': 'நாடி', 'max_points': 8}
}

# Dosha Types
DOSHAS = {
    'mangal': {'name': 'Mangal Dosha', 'tamil': 'மங்கல் தோஷம்'},
    'kala_sarpa': {'name': 'Kala Sarpa Dosha', 'tamil': 'கால சர்ப்ப தோஷம்'},
    'shani': {'name': 'Shani Dosha', 'tamil': 'சனி தோஷம்'},
    'rahu_ketu': {'name': 'Rahu Ketu Dosha', 'tamil': 'ராகு கேது தோஷம்'}
}

# Panchangam Elements
TITHI_NAMES = {
    1: 'Pratipada', 2: 'Dwitiya', 3: 'Tritiya', 4: 'Chaturthi', 5: 'Panchami',
    6: 'Shashthi', 7: 'Saptami', 8: 'Ashtami', 9: 'Navami', 10: 'Dashami',
    11: 'Ekadashi', 12: 'Dwadashi', 13: 'Trayodashi', 14: 'Chaturdashi', 15: 'Purnima/Amavasya'
}

TITHI_NAMES_TAMIL = {
    1: 'பிரதமை', 2: 'துவிதியை', 3: 'திரிதியை', 4: 'சதுர்த்தி', 5: 'பஞ்சமி',
    6: 'சஷ்டி', 7: 'சப்தமி', 8: 'அஷ்டமி', 9: 'நவமி', 10: 'தசமி',
    11: 'ஏகாதசி', 12: 'துவாதசி', 13: 'திரயோதசி', 14: 'சதுர்தசி', 15: 'பௌர்ணமி/அமாவாசை'
}

YOGA_NAMES = {
    1: 'Vishkumbha', 2: 'Preeti', 3: 'Ayushman', 4: 'Saubhagya', 5: 'Shobhana',
    6: 'Atiganda', 7: 'Sukarma', 8: 'Dhriti', 9: 'Shoola', 10: 'Ganda',
    11: 'Vriddhi', 12: 'Dhruva', 13: 'Vyaghata', 14: 'Harshana', 15: 'Vajra',
    16: 'Siddhi', 17: 'Vyatipata', 18: 'Variyana', 19: 'Parigha', 20: 'Shiva',
    21: 'Siddha', 22: 'Sadhya', 23: 'Shubha', 24: 'Shukla', 25: 'Brahma',
    26: 'Indra', 27: 'Vaidhriti'
}

KARANA_NAMES = {
    1: 'Bava', 2: 'Balava', 3: 'Kaulava', 4: 'Taitila', 5: 'Gara',
    6: 'Vanija', 7: 'Vishti', 8: 'Shakuni', 9: 'Chatushpada', 10: 'Naga', 11: 'Kimstughna'
}
