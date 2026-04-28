import http.server
import socketserver
import json
import urllib.parse
import argparse
import re

question_bank = []
question_index = {}

def extract_option_content(option_text):
    """去掉选项字母前缀，提取内容"""
    text = re.sub(r'^[A-Za-z][.、\s]*', '', option_text.strip())
    return text.strip()

def get_answer_content(bank_options, answer_letters):
    """从题库选项中获取答案字母对应的选项内容"""
    for line in bank_options.split('\n'):
        line = line.strip()
        if line:
            letter = line[0]
            if letter in answer_letters:
                return extract_option_content(line)
    return None

def find_in_request_options(request_options, answer_content):
    """在请求选项中精确找到答案内容，返回对应的位置字母"""
    lines = [l.strip() for l in request_options.split('\n') if l.strip()]
    for idx, line in enumerate(lines):
        opt = extract_option_content(line) if line and line[0] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' else line
        if opt == answer_content:
            letter = chr(65 + idx)
            return f"{letter}. {opt}"
    return None

def search_question(title):
    """精确匹配题目"""
    # 先尝试精确匹配
    if title in question_index:
        return question_index[title], 1.0

    # 再尝试包含匹配
    for q in question_bank:
        if title in q['title'] or q['title'] in title:
            return q, 1.0

    return None, 0

class QuestionBankHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        title = params.get('title', [''])[0]
        request_options = params.get('options', [''])[0]
        q_type = params.get('type', [''])[0]

        match, score = search_question(title)

        if match:
            answer_letters = match['answer']

            # 判断题特殊处理
            if match['type'] == 'judgement':
                answer_text = answer_letters
                if answer_text in ['对', '正确']:
                    answer_text = 'A. 对'
                elif answer_text in ['错', '错误']:
                    answer_text = 'B. 错'
                else:
                    if request_options:
                        lines = [l.strip() for l in request_options.split('\n') if l.strip()]
                        for idx, line in enumerate(lines):
                            if answer_text in line or line in answer_text:
                                letter = chr(65 + idx)
                                answer_text = f"{letter}. {line}"
                                break

                response = {
                    "code": 1,
                    "data": {
                        "question": match['title'],
                        "answer": answer_text
                    }
                }
            else:
                # 单选、多选题
                answer_contents = []
                for letter in answer_letters:
                    content = get_answer_content(match['options'], letter)
                    if content:
                        answer_contents.append(content)

                results = []
                if request_options:
                    for content in answer_contents:
                        result = find_in_request_options(request_options, content)
                        if result:
                            results.append(result)

                answer_text = '#'.join(results) if results else '#'.join(answer_contents)

                response = {
                    "code": 1,
                    "data": {
                        "question": match['title'],
                        "answer": answer_text
                    }
                }
        else:
            response = {
                "code": 0,
                "msg": "未找到题目"
            }

        response_data = json.dumps(response, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', len(response_data))
        self.end_headers()
        self.wfile.write(response_data)

    def log_message(self, format, *args):
        print(f"[请求] {args[0]}")

def load_question_bank(path):
    """加载题库"""
    global question_bank, question_index
    with open(path, 'r', encoding='utf-8') as f:
        question_bank = json.load(f)
    question_index = {q['title']: q for q in question_bank}
    print(f"题库加载完成: {path}，共 {len(question_bank)} 道题")

def run_server(port=5000):
    with socketserver.TCPServer(("", port), QuestionBankHandler) as httpd:
        print(f"题库服务器运行在 http://localhost:{port}")
        httpd.serve_forever()

def main():
    parser = argparse.ArgumentParser(description='题库服务器')
    parser.add_argument('-b', '--bank', default='question_bank.json', help='题库JSON文件路径')
    parser.add_argument('-p', '--port', type=int, default=5000, help='服务器端口')
    args = parser.parse_args()

    load_question_bank(args.bank)
    run_server(args.port)

if __name__ == "__main__":
    main()
