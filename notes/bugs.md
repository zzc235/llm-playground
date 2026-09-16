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

---

## 九月十六日 · 本地部署大模型（llama.cpp 线）

### 第 9 条 · 同一台机器，两个命令给出两个显存数字

现象：要跑本地模型，先查硬件。两条命令给出的显存不一致。

报错（其实是两条命令的输出）：
```
# 命令 A
> nvidia-smi
| NVIDIA GeForce RTX 3060 ... |    1599MiB /   6144MiB |

# 命令 B
> Get-CimInstance Win32_VideoController | Select-Object Name, AdapterRAM
Name                               AdapterRAM
----                               ----------
NVIDIA GeForce RTX 3060 Laptop GPU 4293918720     # ≈ 4 GB
```

原因：**WMI 的 `AdapterRAM` 字段是 32 位无符号整数，上限约 4.29 GB。**
显存超过 4 GB 时它会**回绕（wrap around）**，报出一个错误的低位值。
你的真实显存是 6 GB（`nvidia-smi` 是驱动直读，准确）。

解决方案：**查硬件时优先信 `nvidia-smi`**，不要用 WMI 的 `AdapterRAM` 判断显存容量。
（WMI 那条命令查显卡**型号**没问题，查**容量**不可信。）

教训：**两个来源给出矛盾答案时，不是"哪个对"，是"哪个更可信" —— 先搞清数据是怎么来的。**
`nvidia-smi` 直接问驱动；WMI 经过一层 32 位字段转换，会溢出。

---

### 第 10 条 · "不是有效的应用程序" —— 报错说的是字面意思

现象：从 GitHub Release 下载 llama.cpp 的 Windows 包，解压后执行主程序，直接报错。

报错：
```
PS E:\llama\bin> .\llama-cli.exe --version
程序"llama-cli.exe"无法运行: 指定的可执行文件不是此操作系统平台的有效应用程序。
    + CategoryInfo          : ResourceUnavailable: (:) [], ApplicationFailedException
    + FullyQualifiedErrorId : NativeCommandFailed
```

排查过程（**零成本，没装任何工具**）：
```
① 看文件完整性 → 9728 字节，正常；SHA256 可算出，不是坏文件
② 看文件头魔数 → head -c 2 → 4d5a ("MZ")，是合法的 PE 可执行文件
③ 解析 PE 头里的 CPU 架构字段：
    偏移 0x3C 处存的是"PE 头位置"，读出该位置 +4 字节 = Machine 字段
    Machine = 0xaa64  →  ARM64
```

原因：**下载的是 ARM64 版本**（给骁龙本用的），机器是 x86-64，架构不匹配。
Windows 那句"不是此操作系统平台的有效应用程序"**说的是字面意思**，一点没错。

误导点：文件名里同时出现 `arm64` 和 `x64` 两个词，极易看错：
```
llama-b10964-bin-win-arm64-cuda-13.4-x64.zip
                       ^^^^^                       ← 这个才是 CPU 架构（错在这里）
                                  ^^^              ← 这个指的是附带的 CUDA 库是 x64（是干扰项）
```
**判据：看 `win-` 后面紧跟着的那个词** —— `cpu` / `cuda` / `vulkan` 是「用什么跑」，
文件名**最后**的 `x64` / `arm64` 才是「给什么 CPU 用」。

解决方案：删掉全部内容，重新下载 `llama-b10964-bin-win-cuda-13.4-x64.zip`，
解压后 `Machine = 0x8664`（x86-64），`--version` 正常输出。

教训（**这条最值钱**）：
> 遇「不是有效的应用程序」，**先怀疑架构，不要先怀疑杀毒软件或文件损坏**。
> 验证方法：看文件名 `win-` 后面跟什么；或直接读 PE 头（偏移 0x3C → 该处 4 字节 → +4 字节处的 2 字节）。
> **排查不需要下载任何工具，一个十六进制查看就够。**
> 顺序永远是：**先零成本定位，再动手改。**

---

### 第 11 条 · `Missing credentials` —— 空字符串不等于"给了"

现象：把云端脚本改成打本地模型，建客户端时直接报错。

报错：
```
openai.OpenAIError: Missing credentials. Please pass an `api_key`,
`workload_identity`, `admin_api_key`, or set the `OPENAI_API_KEY`
or `OPENAI_ADMIN_KEY` environment variable.
```

原因：`api_key=""`（**空字符串**）在 openai 库看来等于「**没给**」。
任何**非空**字符串（哪怕是无意义的 `"local"`）才算给了。
本地 llama-server 不校验 key，所以填什么都能过，**但不能是空的**。

解决方案：`api_key="local"`。

**附带的判断**：报错里建议你「set the OPENAI_API_KEY environment variable」——
**那是库的兜底路径，不是给你的建议。** 库的查找顺序是：
`api_key` 参数 → `OPENAI_API_KEY` 环境变量 → 都没有才报错。
你的场景根本不需要设那个环境变量。

教训：**报错给的"建议"不一定适合你，要判断它是不是在指路。**

---

### 第 12 条 · 本地收到 401 —— 本地不校验 key，所以一定是地址错了

现象：改完 `api_key` 后仍报错。

报错：
```
openai.AuthenticationError: Error code: 401 - {'error': {'message':
"Authentication Fails, Your api key: ****l',) is invalid",
'type': 'authentication_error', ...}}
```

**关键信号有两个：**

① `Your api key: ****l',)` —— 冒号后面那串东西是 `local",` 的尾巴，
   说明**传进去的是带标点的字符串碎片**，不是干净的 `"local"`。
   （同类线索：`****` 是脱敏前缀，**后面剩下的字符才是真相**）

② `Authentication Fails` + `authentication_error` 这种中英文混杂的措辞，
   **是云端 API 的返回格式**。本地 llama-server 不会长这样。

原因：**本地服务不校验密钥 —— 所以本地场景下收到 401，唯一可能是请求根本没打到本地。**
要么 `base_url` 没改，要么括号写错导致参数传递混乱。

解决方案：核对 `OpenAI(...)` 的括号配对和 `base_url` 的值。
正确形式：
```python
client = OpenAI(
    api_key="local",
    base_url="http://127.0.0.1:8080/v1",
)
```

教训（**推理模式，可复用**）：
> **报错说 A 有问题，但你知道 A 在这个场景下根本不可能有问题 → 那问题一定在别处。**
> 这比"读懂报错在说什么"更进一步，是"判断报错对不对"。

---

### 第 13 条 · `truncated = 1` —— 输出被上下文长度硬切断

现象：本地模型跑通了，输出看着正常，但服务日志里有截断标记。

报错（服务端日志）：
```
slot print_timing: id 3 | task 1706 | prompt eval time = 19.65 ms / 1 tokens
slot print_timing: id 3 | task 1706 |        eval time = 22808.81 ms / 1704 tokens (74.66 tokens per second)
slot print_timing: id 3 | task 1706 |       total time = 22828.46 ms / 1705 tokens
slot      release: id 3 | task 1706 | stop processing: n_tokens = 4095, truncated = 1
                                                                          ^^^^^^^^^^^^ 就是它
```

原因：**输入 + 输出 撞上了 `-c` 设定的上下文上限。** 拆解：
```
-c 4096 的总额度 = 4096 tokens
  输入（system + prompt + 油库笔记）= 2392 tokens  (58%)
  输出（模型的回答）              = 1704 tokens  (42%)
  合计                            = 4096 tokens  ← 撞顶
```
模型正在逐条核对笔记，**还没写完就被强行切断**，且**脚本这边不会报错**——
`f.write(answer)` 照样把半截内容写进 `output.txt`。**又是一次静默失败。**

解决方案（两选一）：
1. 加大上下文：启动时 `-c 8192`（Qwen3-4B 原生支持 32768，8192 完全在能力内）
2. 缩短输入：不要一次喂整份笔记，分段核对

教训：
> **上下文（`-c`）是「输入 + 输出」共享的一个额度，不是只给输入的。**
> 输入长了，输出空间就被压缩 —— 这个现象叫"上下文挤占"。
> **判断方法：看服务日志里的 `truncated` 字段，它不会主动告诉你，要自己看。**
> 又一次印证：**不报错的失败，比报错的失败危险。**

---

## 九月十六日 · 本地部署的完整验证数据（存档用）

| 项 | 值 |
|---|---|
| 硬件 | RTX 3060 Laptop GPU，**6 GB 显存**，16 GB 内存 |
| 驱动 / CUDA | 591.74 / CUDA 13.1 |
| llama.cpp | `version: 0.4.1-dev (build 10964, commit b29c606e2)`，Clang 20.1.8，**x86_64** |
| 包 | `llama-b10964-bin-win-cuda-13.4-x64.zip` + `cudart-llama-bin-win-cuda-13.4-x64.zip` |
| 模型 | `Qwen3-4B-Q4_K_M.gguf`（2,497,281,312 字节 ≈ 2.33 GB，魔数 `47475546` = "GGUF"） |
| 启动命令 | `llama-server.exe -m E:\llama\models\Qwen3-4B-Q4_K_M.gguf -ngl 99 -c 4096 --port 8080` |
| 显存占用 | 1599 MiB → **5349 MiB**（模型全部 36 层上 GPU） |
| **读取速度** | **2535 tokens/s**（prompt eval，并行计算） |
| **生成速度** | **75-77 tokens/s**（eval，串行生成） |
| 上下文 | 4096（**不够，见第 13 条**） |

**速度指标怎么读**（`llama-server` 日志）：

| 字段 | 含义 |
|---|---|
| **`tg = 75.98 t/s`** | 实时生成速度（token generation）—— **最常看的指标** |
| `tg_3s` | 最近 3 秒的瞬时速度 |
| `prompt eval time` | 读入速度（并行，通常几百到几千 t/s） |
| `eval time` | 整次请求的平均生成速度（串行） |
| `truncated` | 是否被上下文截断（**0 = 正常，1 = 被切**） |

**为什么生成速度会缓慢下降**（77.24 → 76.10）：
token 越往后，KV cache 越大，注意力计算越重。**正常现象，不是性能问题。**

---

## 九月十六日教训（新增）

看到 `不是有效的应用程序` → **先查架构**（PE 头偏移 0x3C），别先怀疑杀毒软件
看到报错建议你设环境变量 → **判断它是兜底路径还是给你的建议**，别照做
看到 `401` 但你知道密码本来就不校验 → **问题一定在地址上**
看到程序"跑完了没报错" → **问一句"我怎么知道它这次是对的"**，去日志里找 `truncated`
**两个来源给出矛盾答案时** → 不是"哪个对"，是"**哪个更可信**"（追问数据是怎么来的）



