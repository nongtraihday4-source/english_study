import re

def parse_topics(text):
    # Match numbered topics: "10. Danh từ ... - 100 câu"
    pattern1 = r'(\d{1,2}\.\s+.*?)\s*-\s*(\d+)\s*[Cc][âa]u'
    matches1 = re.findall(pattern1, text)
    
    # Match unnumbered topics (the first 9)
    # They start with "Thì", "Nhóm thì", or "Sự hòa hợp"
    pattern2 = r'((?:Thì|Nhóm thì|Sự hòa hợp)\s+.*?)\s*-\s*(\d+)\s*[Cc][âa]u'
    matches2 = re.findall(pattern2, text)
    
    all_matches = matches2 + matches1
    
    # The output needs to preserve order? We can just finditer to keep order.
    pattern_combined = r'((?:\d{1,2}\.\s+|(?:Thì|Nhóm thì|Sự hòa hợp)\s+).*?)\s*-\s*(\d+)\s*[Cc][âa]u'
    
    results = []
    for match in re.finditer(pattern_combined, text):
        topic = match.group(1).strip()
        count = match.group(2).strip()
        results.append((topic, count))
        
    return results

with open('/home/n2t/Documents/english_study/prompt/Danh sách 50 chuyên đề với tổng 5,000 câu.md', 'r', encoding='utf-8') as f:
    text = f.read()

r = parse_topics(text)
for i, x in enumerate(r):
    print(f"{i+1}: {x[0]} -> {x[1]}")
