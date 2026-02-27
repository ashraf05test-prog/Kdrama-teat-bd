import re
from deep_translator import GoogleTranslator
import google.generativeai as genai

def convert_vtt_to_srt(vtt_text):
    lines = vtt_text.split('\n')
    srt_lines = []
    index = 1
    in_block = False
    
    for line in lines:
        line = line.strip()
        if not line:
            if in_block:
                srt_lines.append("")
                in_block = False
            continue
            
        if line.upper() == "WEBVTT" or line.upper().startswith("NOTE") or line.startswith("X-TIMESTAMP-MAP"):
            continue
            
        if "-->" in line:
            line = line.replace('.', ',')
            if not in_block:
                srt_lines.append(str(index))
                index += 1
                in_block = True
            srt_lines.append(line)
        elif in_block:
            srt_lines.append(line)
            
    return "\n".join(srt_lines)

def parse_srt(srt_text):
    blocks = re.split(r'\n\s*\n', srt_text.strip())
    parsed = []
    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            idx = lines[0].strip()
            ts = lines[1].strip()
            text = "\n".join(lines[2:]).strip()
            parsed.append((idx, ts, text))
    return parsed

def translate_google(srt_text, dest_lang='bn'):
    translator = GoogleTranslator(source='en', target=dest_lang)
    parsed = parse_srt(srt_text)
    translated_srt = []
    
    batch_texts = []
    batch_indices = []
    
    for i, (idx, ts, text) in enumerate(parsed):
        batch_texts.append(text)
        batch_indices.append((idx, ts))
        
        if len(batch_texts) == 20 or i == len(parsed) - 1:
            try:
                translated_batch = translator.translate_batch(batch_texts)
                for j, (b_idx, b_ts) in enumerate(batch_indices):
                    translated_srt.append(f"{b_idx}\n{b_ts}\n{translated_batch[j]}")
                translated_srt.append("")
            except Exception as e:
                print(f"Google translate batch error: {e}")
                for j, (b_idx, b_ts) in enumerate(batch_indices):
                    translated_srt.append(f"{b_idx}\n{b_ts}\n{batch_texts[j]}")
                translated_srt.append("")
                
            batch_texts = []
            batch_indices = []
            
    return "\n".join(translated_srt)

def translate_gemini(srt_text, api_key, dest_lang='bn'):
    if not api_key:
        return translate_google(srt_text, dest_lang)
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        parsed = parse_srt(srt_text)
        prompt = f"Translate the following subtitle texts to {dest_lang}. Keep the exact same numbering and only output the numbered translated text.\n\n"
        
        for idx, ts, text in parsed:
            prompt += f"[{idx}] {text}\n"
            
        response = model.generate_content(prompt)
        res_text = response.text
        
        translated_dict = {}
        for line in res_text.split('\n'):
            match = re.match(r'\[(\d+)\]\s*(.*)', line)
            if match:
                translated_dict[match.group(1)] = match.group(2)
                
        translated_srt = []
        for idx, ts, text in parsed:
            t_text = translated_dict.get(idx, text)
            translated_srt.append(f"{idx}\n{ts}\n{t_text}\n")
            
        return "\n".join(translated_srt)
    except Exception as e:
        print(f"Gemini translation failed: {e}. Falling back to Google Translate.")
        return translate_google(srt_text, dest_lang)
