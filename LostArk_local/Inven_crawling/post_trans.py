import pandas as pd
import json

# CSV 파일 읽기
file_path = 'post_data.csv'
data = pd.read_csv(file_path)
# JSON 변환 함수
def convert_to_json(df):
    json_data = []
    for _, row in df.iterrows():
        # 댓글 데이터 파싱
        try:
            comments = eval(row['comments']) if isinstance(row['comments'], str) else row['comments']
        except:
            comments = []

        # JSON 형식으로 저장
        json_data.append({
            "title": row['title'],
            "content": row['content'],
            "comments": comments  # 이미 구조화된 데이터를 그대로 사용
        })
    return json_data

# JSON 변환 실행
structured_data = convert_to_json(data)

# JSON 저장
output_path = 'post_data_json.csv'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(structured_data, f, ensure_ascii=False, indent=4)

print(f"구조화된 JSON 파일이 저장되었습니다: {output_path}")
