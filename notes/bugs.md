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

### 第 14 条 · HTTP 500 `Context size has been exceeded` —— 改了 `-c` 还是撞顶

现象：第 13 条发现 `truncated = 1` 后，把启动命令的 `-c 4096` 改成了 `-c 8192`，重启服务，
**结果这次直接报错了**——而且是从 VSCode 那边抛出来的。

报错（VSCode / Python 端）：
```
openai.InternalServerError: Error code: 500 - {'error': {'code': 500,
  'message': 'Context size has been exceeded.', 'type': 'server_error'}}
```

报错（服务端日志，同一次请求）：
```
W decode: failed to find a memory slot for batch of size 2
W decode: failed to find a free space in the KV cache for batch of size 2
W decode:  - n_batch = 1024, n_ctx = 8192, n_kv    = 8192, n_keep = 1, n_past = 3506
W decode:  - slot 0: n_ctx_slot = 4096, n_past = 3502, n_ctx_used = 3502
...
E decode: Context size has been exceeded.
```

### 这条报错怎么读（关键：只看一行）

日志里信息量最大的是这一行：
```
W decode: - slot 0: n_ctx_slot = 4096, n_past = 3502, n_ctx_used = 3502
                       ^^^^^^^^^^^^^^^^^^  这个槽实际只有 4096 额度
```

**明明 `-c 8192`，为什么槽只有 4096？** 因为启动命令里还有 `--parallel 4`（默认值）。

### 原因：`n_slots` 把 `-c` 瓜分了

```
-c 8192  ÷  n_slots = 4  =  每个槽 4096
```

上下文总量是**所有并发槽共享**的一个池子，不是每槽各给 8192。
槽位拿到 4096，而这次请求的输入就已经 3502 token 了 —— 加上要生成的输出，瞬间撑爆。

### 引擎的三级降级过程（日志逐行对应）

llama.cpp 撞上空间不足时不会立刻放弃，它会**一层层往下退**：

| 顺序 | 日志 | 它在干什么 |
|---|---|---|
| 1 | `batch of size 2` | 原始批量 |
| 2 | `n_batch = 1024` | 把批量切成 1024 再试 |
| 3 | （再切更小） | 继续切 |
| 4 | `E decode: Context size has been exceeded.` | 退无可退，报错 |

**注意方向**：它是把**批量**切小（一次处理更少的 token），
但**问题不是批量太大**，是**池子本身装不下**。所以切批量无效，最后只能报 500。

⚠️ **这正是排查时最容易走偏的地方**：日志一直在说 `batch`，
但真正的数字在 `n_ctx_slot` 那一行。**对着最响的噪音排查，是浪费时间。**

### 解决方案

```powershell
.\llama-server.exe -m E:\llama\models\Qwen3-4B-Q4_K_M.gguf `
  -ngl 99 -c 8192 --parallel 1 `
  --cache-type-k q8_0 --cache-type-v q8_0 `
  --port 8080
```

两处改动：
- `--parallel 1` —— 单槽，**独吞整个 8192**
- `--cache-type-k/v q8_0` —— KV cache 量化到 8 位，**显存占用减半**，给上下文腾地方

**验证方法**：重启后看日志，必须出现
```
n_slots = 1, n_ctx_slot = 8192
```
看到 `n_ctx_slot = 8192` 才算真的生效。**改完不算完，要验证。**

### 关于 HTTP 状态码：知道 4xx / 5xx 就能省一半排查功夫

| 段 | 含义 | 责任方 | 你该看哪 |
|---|---|---|---|
| `4xx` | 客户端错误 | **你自己** | 你的代码、参数、地址 |
| `5xx` | 服务端错误 | **对方** | 服务端日志、配置 |

具体到这几条实战：

| 报错 | 码 | 谁的问题 |
|---|---|---|
| `Missing credentials` | — | 你的代码（库自己抛的，不是 HTTP） |
| `AuthenticationError 401` | 4xx | 你的地址（本地不校验 key，见第 12 条） |
| `InternalServerError 500` | 5xx | **服务端**——你的 Python 代码没问题，去翻 llama-server 的日志 |

### 教训

> **看到 `500` 或 `InternalServerError`，别去看自己的代码。** 那是服务端在说"我顶不住了"，
> 你的脚本只是**传话人**，它没写错。往服务端日志走。

> **`-c` 不是每槽各给一份，是全场共享。** 多了一个 `--parallel`，
> 每个请求实际能用的额度就除以槽数。**配置项之间有乘法关系，不是加法。**

> **报错里喊得最响的那句，往往不是根因。** 这次日志满屏是 `batch size`，
> 真凶藏在 `n_ctx_slot` 那一行不显眼的数字里。

> **改完配置要验证，不看日志等于没改。** 这次"改了 `-c` 还是报错"，
> 如果第一条就去看 `n_ctx_slot` 是多少，能省下整轮排查。

> **错误是分层的：4xx 查自己，5xx 查对方。** 记住这一条，
> 以后所有 HTTP 报错都能**先定位到哪一层**，再谈具体原因。

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
看到 `500` / `InternalServerError` → **服务端的问题，不要去看自己的代码**，去翻服务端日志
看到 `Context size has been exceeded` → **先查 `n_slots` 是不是把 `-c` 瓜分了**（`-c ÷ n_slots = 每槽额度`）
改了配置之后 → **不看日志验证，等于没改**
**两个来源给出矛盾答案时** → 不是"哪个对"，是"**哪个更可信**"（追问数据是怎么来的）

---

# 九月十九日 · 工程化改造 review 挖出的三个预埋缺陷

> ⚠️ **这三条和前面 14 条性质不同：它们还没有触发过。**
> 是代码 review 提前挖出来的，下面的报错文本是**预期值**，真触发后要回来补录原文。
>
> 记它们的原因很简单：**其中第一条的同类版本你 09-16 已经踩过一次（第 12 条），
> 但这次没把那条教训写进代码里。**

---

### 第 15 条 · `base_url` 没校验 —— 401 的同一个坑，换了个地方埋

**位置**：`llm_client.py` 第 15–22 行

```python
api_key  = os.getenv("DEEPSEEK_API_KEY")   # 有检查（但检查方式见第 16 条）
base_url = os.getenv("BASE_URL")           # ← 一个字都没管
client = OpenAI(api_key=api_key, base_url=base_url)
```

**现象**：`BASE_URL` 拼错、漏配，或者哪天在 `.env` 里改了名字 →
`base_url` 拿到 `None` → **程序不报错**，照常启动、照常发请求。

**原因**：OpenAI SDK 在 `base_url=None` 时**不抛异常**，它默默退回默认地址
`https://api.openai.com/v1`。于是你拿着 DeepSeek 的 key 去敲 OpenAI 的门。

**预期报错（待触发后补录原文）**：
```
openai.AuthenticationError: Error code: 401
```

**⚠️ 和第 12 条是同一个规律**：

| 条目 | 场景 | 401 的真正原因 |
|---|---|---|
| 第 12 条 | 本地 llama-server | 本地不校验 key → **请求根本没打到本地** |
| 第 15 条 | 云端 DeepSeek | SDK 帮你兜底 → **请求打到了别的地址** |

**两次都是：看到 401，先怀疑地址，不是 key。**

**修正方案**（状态：待修）：三个 env 一视同仁全查，不许有裸奔的。
```python
for name in ("DEEPSEEK_API_KEY", "BASE_URL", "MODEL_NAME"):
    if not os.getenv(name):
        raise RuntimeError(f"缺少环境变量 {name}，请检查 .env 文件")
```

**教训**：
> **有默认值的东西，坏起来是静默的。**
> `model_name` 给了默认值（这是对的），但 `base_url` 毫无保护 ——
> 而它恰好是**错了也不报错**的那一个，因为 SDK 会帮你兜底。
> **兜底兜错了方向，比不兜底更危险。**

---

### 第 16 条 · 「打了一行 error 日志」不等于「早失败」

**位置**：`llm_client.py` 第 19–22 行

```python
if not api_key:
    logger.error("未找到 DEEPSEEK_API_KEY，请检查 .env 文件！")
    # ← 没有 raise，程序继续往下跑
client = OpenAI(api_key=api_key, base_url=base_url)
```

**现象**：`.env` 里没有 key 时，日志里确实出现了你写的那句中文提示 ——
**但程序没有停，它继续建 client。**

**原因**：`logger.error()` 只负责**记录**，不负责**中断**。
日志是行车记录仪，不是刹车。

**实际发生的事情**（预期报错）：
```
openai.OpenAIError: The api_key client option must be set either by passing
api_key to the client or by setting the OPENAI_API_KEY environment variable
```

崩确实会崩 —— 但**崩出来的是 SDK 的英文报错，你精心写的中文提示等于白打了**。
自己写的错误信息只有配合 `raise` 才有价值。

**修正方案**（状态：待修）：二选一，别混用。
```python
# 方案 A：自己抛，错误信息归你控制
if not api_key:
    raise RuntimeError("未找到 DEEPSEEK_API_KEY，请检查 .env 文件")

# 方案 B：干脆不用 getenv，取不到直接 KeyError
api_key = os.environ["DEEPSEEK_API_KEY"]
```

**教训**：
> **日志不是刹车。** 想「早失败」，就必须有一个 `raise`（或 `sys.exit`）——
> 只打日志然后往下跑，等于什么都没做。
>
> 判断标准一句话：**程序有没有停在这一行？** 没停，就不是早失败。

---

### 第 17 条 · `retry` 没筛异常 —— 把不该重试的错也重试了 3 次

**位置**：`llm_client.py` 第 26–30 行

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
#                                                                 ^^^^^^^^^^^^^^^^^^^^^^^
#                                                                 导进来了，一次都没用

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True          # ← retry= 这个参数没给
)
```

**现象**：不带 `retry=` 参数时，tenacity 默认**任何异常都重试**。

**原因**：重试**只对「临时性故障」有意义**。把永久性错误也重试，结果是
白白烧掉 3 次请求 + 约 4 秒等待，还把真正的错误信息埋进日志里。

| 异常 | 该不该重试 | 为什么 |
|---|---|---|
| 429 限流 | ✅ 该 | 等一下真会好 |
| 500 / 502 / 503 | ✅ 该 | 服务端抖动 |
| 超时 / 连接断开 | ✅ 该 | 网络问题，重试有意义 |
| **400 参数错** | ❌ **不该** | prompt 格式错了，重试 3 次还是 400 |
| **401 认证错** | ❌ **不该** | key 或地址错了，重试 3 次还是 401 |
| **`TypeError`** | ❌ **不该** | 自己代码的 bug，等一万年也一样 |

**修正方向**（状态：待修）：给 `retry=` 传 `retry_if_exception_type(...)`，
只圈出**临时性异常**。方向：去 `openai` 库里找现成的异常类，
按「429 / 5xx / 超时」这三类去筛。

**教训**：
> **判断规则一句话：「等一下再试，有没有可能好？」**
> 答案是「否」→ 不重试。
>
> 另外：**import 了却没用，是代码在给你留线索。**
> `retry_if_exception_type` 出现在第 4 行，说明写的时候想过这件事，
> 只是没走到最后一步。以后看到"导了没用"的包，回头问一句「我本来打算干嘛」。

---

## 九月十九日教训（速查）

| 看到什么 | 先想什么 |
|---|---|
| 有 `default=` 或有 SDK 兜底的配置项 | **它错了会不会报错？** 不会 → 必须自己校验（第 15 条） |
| 打了 `logger.error` 但程序继续跑 | **这不是早失败。** 没 `raise` 就是没停（第 16 条） |
| 看到 401 | **先怀疑地址，不是 key**（第 12 条 / 第 15 条通用） |
| 写重试逻辑 | **先问「等一下再试有没有可能好」**，再决定哪些异常进重试圈（第 17 条） |
| 发现自己 import 了没用的东西 | 那是**写的时候想过、但没做完**的信号，回去补（第 17 条） |
| 提交代码前 | message 写**改了什么**，不写「谁帮的忙」、不写「今日成果」 |




