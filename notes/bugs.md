### 第一次git合并提交测试
现象：点击commit被GitHub上的库拒绝合并
原因：是两条历史没有共同祖先——远端建库时勾了初始化选项，生成了一个 Initial commit；你本地是另一个 init comit。两者毫无血缘关系，git 拒绝拼在一起。
报错：暂时找不到
解决方案 git remote rename github-test origin
git pull origin main --allow-unrelated-histories --no-edit
git push -u origin main
注意：git 的提示信息会骗人。它说你的分支"behind 远端"，实测其实是"分叉"。这种情况 git 复用同一套提示模板。
### 今日调用api测试
现象：调用模型频繁报错
报错："""File "e:\code\llm-playground\main.py", line 3, in <module>
    from deepseek import DeepSeek
ModuleNotFoundError: No module named 'deepseek'"""
原因：ModuleNotFoundError: No module named 'xxx' = 你的环境里没有可以 import 的、名叫 xxx 的包。​
这时该做的第一件事不是猜，是去查这个名字到底存不存在（比如搜 "DeepSeek official python sdk"）
解决方案：改用open ai的依赖库
补充报错："""File "e:\code\llm-playground\main.py", line 8, in <module>
    client = DeepSeek(api_key=api_key,base_url=Base_URL,model=model)
             ^^^^^^^^
NameError: name 'DeepSeek' is not defined"""
### 关于客户端构建
现象：启动失败，直接报错
报错： """File "e:\code\llm-playground\main.py", line 11
    response = client.chat.completions.create(
                                             ^
SyntaxError: '(' was never closed"""
原因：依旧是python的语法错误，括号没有封闭导致界限没有划分清晰
解决方案：检查完语法后补齐
### 构建客户端时误赛模型model
现象：测试时启动不能，直接报错
报错： """ File "e:\code\llm-playground\main.py", line 8, in <module>
    client = OpenAI(api_key=api_key,base_url=Base_URL,model=model)
TypeError: OpenAI.__init__() got an unexpected keyword argument 'model'"""
原因：构建客户端时不需要直接调用模型，只需要api和base_url即可
解决方案：将model调用删除，检查完语法后括号封闭
### 依旧构建客户端时用户输入变量定义
现象：拒绝启动并直接报错
报错： """ File "e:\code\llm-playground\main.py", line 14
    {"role": "system", "content": (variable) user_input: str}
                                   ^^^^^^^^^^^^^^^^^^^^
SyntaxError: invalid syntax. Perhaps you forgot a comma? """
原因：将类型注解塞进变量定义中
解决方案：删除str和variable并修改content。
### 字典编写message
现象：添加的参数直接标红报错
报错：""" File "e:\code\llm-playground\main.py", line 14, in <module>
    {"role": "system", "content": "你的名字叫测试集1号"},{"role":"user","content":user_input} (user_input= "你叫什么名字")
                                                         ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: 'dict' object is not callable """
原因：字典无法被定义，变量的定义应该在字典外面定义
解决方法：删除并修改结构，选择用f+string格式实现这个输入内容可以被变量赋值并运行
### 构建f+string 结构时格式错误
现象：使用换行符\n时报错
原因：「相邻字面量 + f 前缀」静默不插值 —— 你第 7 条的解法是 f"..."+f"..."，它修好了 SyntaxError，但引入了这个新问题：{user_input} 没被替换，模型收到了字面量 {user_input}，而程序一声不吭。
第二条比 SyntaxError 危险得多——SyntaxError 会当场拦住你，静默失败会让你把错的结果当成对的用。
报错： """File "e:\code\llm-playground\main.py", line 11
    prompt = f"请回答测试内容"\n{user_input}"
                        ^
SyntaxError: unexpected character after line continuation character """
解决方案：以f+string +f+string的格式达成我想使用输入的user_input完成连通性测试
### 九月十五日教训
看到 SyntaxError: xxx was never closed → 别慌，Python 已经给了行号和 ^，往上找没配对的括号
看到报错里的 Perhaps you forgot... / hint: → 那是猜测，不是诊断（你那条 git 的"提示会骗人"是同一类现象）



