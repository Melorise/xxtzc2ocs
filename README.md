# xxtzc2ocs
学习通自测题转ocs网课助手题库

## 使用方式
### 1.在浏览器打开你的自测题查看详情页，右键网页另存为，不要修改文件名
### 2.克隆本仓库到本地
使用方法：
#### 提取题库：
  ```python
  #从文件夹提取
  python extract_questions.py 1 -o bank1.json
  python extract_questions.py 2 -o bank2.json
  python extract_questions.py 3 -o bank3.json
  #或从HTML文件提取
  python extract_questions.py path/to/查看详情.html -o my_bank.json
  ```

#### 启动服务器：
  ```python
  # 使用默认题库 question_bank.json
  python server.py
  # 指定题库和端口
  python server.py -b bank3.json -p 5001
  python server.py -b bank1.json -p 5002
  ```
### 3.配置OCS
  找到全局设置里的题库配置，把question_bank_config.json里的内容粘贴进去
