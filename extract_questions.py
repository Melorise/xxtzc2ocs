import re
import json
import os
import html
import argparse

def parse_html(file_path):
    """解析HTML文件，提取题目和答案"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    questions = []

    # 按题目块分割
    question_blocks = re.split(r'<div class="marBom60 questionLi', content)[1:]

    for block in question_blocks:
        try:
            # 提取题目类型
            type_match = re.search(r'\(单选题\)|\(多选题\)|\(判断题\)', block)
            q_type = 'unknown'
            if type_match:
                type_text = type_match.group()
                if '单选题' in type_text:
                    q_type = 'single'
                elif '多选题' in type_text:
                    q_type = 'multiple'
                elif '判断题' in type_text:
                    q_type = 'judgement'

            # 提取题目内容
            title_match = re.search(r'<span class="qtContent">(.*?)</span>', block, re.DOTALL)
            title = ''
            if title_match:
                title = clean_html(title_match.group(1))

            # 提取选项
            options_match = re.search(r'<ul class="mark_letter[^"]*"[^>]*>(.*?)</ul>', block, re.DOTALL)
            options = []
            if options_match:
                li_matches = re.findall(r'<li[^>]*>(.*?)</li>', options_match.group(1), re.DOTALL)
                for li in li_matches:
                    opt = clean_html(li)
                    if opt:
                        options.append(opt)

            # 提取正确答案
            answer_match = re.search(r'<span class="rightAnswerContent">([^<]+)</span>', block)
            answer = ''
            if answer_match:
                answer = answer_match.group(1).strip()

            if title and answer:
                questions.append({
                    'type': q_type,
                    'title': title,
                    'options': '\n'.join(options),
                    'answer': answer
                })
        except Exception as e:
            print(f"解析题目出错: {e}")
            continue

    return questions

def clean_html(text):
    """清理HTML标签和特殊字符"""
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def main():
    parser = argparse.ArgumentParser(description='从HTML提取题库')
    parser.add_argument('input', help='输入HTML文件或文件夹路径')
    parser.add_argument('-o', '--output', default='question_bank.json', help='输出JSON文件路径')
    args = parser.parse_args()

    all_questions = []
    input_path = args.input

    if os.path.isfile(input_path):
        # 单个文件
        print(f"正在解析: {input_path}")
        questions = parse_html(input_path)
        all_questions.extend(questions)
    elif os.path.isdir(input_path):
        # 文件夹，查找查看详情.html
        html_file = os.path.join(input_path, '查看详情.html')
        if os.path.exists(html_file):
            print(f"正在解析: {html_file}")
            questions = parse_html(html_file)
            all_questions.extend(questions)
        else:
            print(f"错误: 文件夹中未找到 查看详情.html")
            return
    else:
        print(f"错误: 路径不存在 {input_path}")
        return

    # 保存
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=2)
    print(f"题库已保存: {args.output}，共 {len(all_questions)} 道题")

if __name__ == '__main__':
    main()
