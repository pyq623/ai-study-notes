# 单元② · 线性代数基础

**本单元目标**：先会“看形状”，再会“算数”，最后理解秩、可逆和方程解之间的关系。矩阵并非一串需要背诵的性质，它首先是一个线性变换的记账方式。

## 1. 标量、向量、矩阵与维度

### 先看一个数、一列数和一张数表

**标量**是一个数，如3、−2、0.5。**向量**是一组有顺序的数。例如把2、5、1排成一列：

$$\mathbf x=\begin{pmatrix}2\\5\\1\end{pmatrix}=(2,5,1)^{\mathsf T}$$

它有3个分量，称**3维列向量**，形状是3行1列，即 $3\times1$。若横排成一行 $(2,5,1)$，就是形状 $1\times3$ 的行向量。上标 $\mathsf T$ 表示转置，把行与列互换，第3节会继续讲。

**矩阵**是按行、列排好的数表。例如：

$$A=\begin{pmatrix}1&2&3\\4&5&6\end{pmatrix}\in\mathbb R^{2\times3}$$

$\mathbb R$ 代表实数，$\in$ 读作“属于”，$\mathbb R^{2\times3}$ 表示由实数组成的2行3列矩阵的集合。一般写 $A\in\mathbb R^{m\times n}$，m是行数，n是列数，**先行后列**。

- **行横着看**：第一行是1、2、3；第二行是4、5、6。
- **列竖着看**：第一列是1、4；第二列是2、5；第三列是3、6。
- 共有 $2\times3=6$ 个元素；元素 $a_{ij}$ 表示第i行、第j列的数。例如 $a_{12}=2$，$a_{23}=6$。

本节先把“形状”理解为几行几列；后面讲到“列空间维数”时，会用秩来计算，那是另一个概念。

### 矩阵加法：同样的位置相加

先给出另一个同为 $2\times3$ 的矩阵：

$$B=\begin{pmatrix}10&20&30\\40&50&60\end{pmatrix}$$

A与B的行数相同、列数也相同，因此每个位置都能一一对应：

$$A+B=\begin{pmatrix}1+10&2+20&3+30\\4+40&5+50&6+60\end{pmatrix}=\begin{pmatrix}11&22&33\\44&55&66\end{pmatrix}$$

例如左上角是A的左上角1加B的左上角10，得到11；第二行第三列是6+60，得到66。结果仍是2行3列，**加法不会把两张数表拼成更大的表**。

若C是3行2列，虽然A与C都有6个元素，它们的形状不同，普通矩阵加法 $A+C$ 没有定义。不能只比较元素总数。

### 矩阵减法：同样的位置相减，注意顺序

仍用刚才的A与B：

$$A-B=\begin{pmatrix}1-10&2-20&3-30\\4-40&5-50&6-60\end{pmatrix}=\begin{pmatrix}-9&-18&-27\\-36&-45&-54\end{pmatrix}$$

相减也要求形状相同，结果形状不变。$B-A$ 会得到相反数，通常 $A-B\ne B-A$。

### 数乘：让每个元素都乘同一个数

在 $2A$ 中，2是标量，意思是**A的每一个元素都乘2**：

$$2A=2\begin{pmatrix}1&2&3\\4&5&6\end{pmatrix}=\begin{pmatrix}2\times1&2\times2&2\times3\\2\times4&2\times5&2\times6\end{pmatrix}=\begin{pmatrix}2&4&6\\8&10&12\end{pmatrix}$$

结果仍是 $2\times3$：变化的是各元素的值，行列数不变。一般 $cA$ 的第i行第j列为 $ca_{ij}$，c是同一个标量。比如 $-A$ 把所有元素取相反数，$0A$ 得到同形状的全零矩阵。

这里的“2×A”属于数乘；下一节的“矩阵×矩阵”则按一行对一列求和，计算规则要分别学习。

### 广播：代码如何把小数组用于多个位置

在NumPy等数组计算库中，某些形状不同的数组仍能做逐元素运算，这种扩展约定叫**广播**。例如A形状为(2,3)，另有一行数r，形状为(1,3)：

$$r=\begin{pmatrix}10&20&30\end{pmatrix}$$

按广播约定，相当于把这一行用于A的每一行，再逐位置相加：

$$r_{\mathrm{expanded}}=\begin{pmatrix}10&20&30\\10&20&30\end{pmatrix}$$

$$A+r_{\mathrm{expanded}}=\begin{pmatrix}1+10&2+20&3+30\\4+10&5+20&6+30\end{pmatrix}=\begin{pmatrix}11&22&33\\14&25&36\end{pmatrix}$$

“扩展成两行”是帮助理解的示意，不意味着程序必须真的复制一份数据。NumPy从形状的最右侧逐维比较：对应维度相等，或其中一个为1，才兼容；缺少的前导维度按1处理。因此(2,3)与(1,3)可广播，(2,3)与(3,2)不兼容。[NumPy广播规则](https://numpy.org/doc/stable/user/basics.broadcasting.html)

按这种代码约定，A+2也可表示每个元素都加2；但在普通矩阵代数中，不能默认把矩阵加标量或矩阵加一行向量解释成广播。**题目写明NumPy／广播规则时照规则算；只问普通矩阵加法时，先要求形状相同。**

### 用一张表区分这些运算

| 写法 | 本节中的含义 | 结果形状 |
| --- | --- | --- |
| $A+B$ | 同形状矩阵，对应位置相加 | 与A相同 |
| $A-B$ | 同形状矩阵，对应位置相减 | 与A相同 |
| $2A$ | 每个元素乘2 | 与A相同 |
| 代码中的A+2 | 若采用标量广播，每个元素加2 | 与A相同 |
| $AB$ | 矩阵乘法，一行对一列相乘求和 | 按下一节的内侧维度规则判断 |

自查：$2A$ 左上角变成多少？第二行第三列变成多少？答案是2和12；它没有把A变成4行或6列。

## 2. 点积与矩阵乘法：一行对一列

两个等长向量的点积，是对应分量相乘再相加。例如 $(1,2)\cdot(3,4)=1\times3+2\times4=11$。

矩阵乘法每个结果元素也按这个规则算：

$$A_{m\times n}B_{n\times p}=C_{m\times p},\qquad c_{ij}=\sum_{k=1}^{n}a_{ik}b_{kj}$$

$m$、$n$、$p$ 是维度，$k$ 遍历参与求和的位置。**内侧维度相同才可乘，结果保留外侧维度。**

**带算例**：

$$\begin{pmatrix}1&2\\3&4\end{pmatrix}\begin{pmatrix}5\\6\end{pmatrix}
=\begin{pmatrix}1\times5+2\times6\\3\times5+4\times6\end{pmatrix}
=\begin{pmatrix}17\\39\end{pmatrix}$$

这是2×2乘2×1，结果2×1。它不是逐元素乘法。

矩阵 $A\in\mathbb R^{m\times n}$ 也可以理解为：把 $n$ 维输入 $\mathbf x$ 变为 $m$ 维输出 $A\mathbf x$。

### 结合律：可以改括号，不能借机换顺序

在维度合法时，矩阵乘法满足：

$$ (AB)C=A(BC) $$

左边先算AB，再乘C；右边先算BC，再让A乘结果。两边的**因子顺序始终是A、B、C**，只是先计算哪一步不同。

**完整例子**：另取两张2×2矩阵和一个2维列向量：

$$P=\begin{pmatrix}1&1\\0&1\end{pmatrix},\quad Q=\begin{pmatrix}2&0\\0&3\end{pmatrix},\quad \mathbf v=\begin{pmatrix}1\\2\end{pmatrix}$$

先算PQ，再乘向量：

$$PQ=\begin{pmatrix}2&3\\0&3\end{pmatrix},\qquad (PQ)\mathbf v=\begin{pmatrix}2\times1+3\times2\\0\times1+3\times2\end{pmatrix}=\begin{pmatrix}8\\6\end{pmatrix}$$

换一种括号，先算Q乘向量：

$$Q\mathbf v=\begin{pmatrix}2\\6\end{pmatrix},\qquad P(Q\mathbf v)=\begin{pmatrix}1\times2+1\times6\\0\times2+1\times6\end{pmatrix}=\begin{pmatrix}8\\6\end{pmatrix}$$

结果相同，所以本例验证了 $(PQ)\mathbf v=P(Q\mathbf v)$。实际计算可在保持因子顺序的前提下，选择中间结果更小的括号，减少运算和存储。

### 交换律：矩阵乘法一般不满足

上例中，反过来乘得到：

$$QP=\begin{pmatrix}2&2\\0&3\end{pmatrix}\ne\begin{pmatrix}2&3\\0&3\end{pmatrix}=PQ$$

所以结合律不意味着 $PQ=QP$。有时AB能算而BA连维度都不合法；即使两者都能算，也不能默认相等。

### 分配律：括号里的和可以展开

在各项维度合法时：

$$A(B+C)=AB+AC,\qquad (A+B)C=AC+BC$$

保持左乘或右乘的位置。例如 $(A+B)C$ 中，C原来在右边，展开后仍分别在A、B的右边。不要凭数字乘法的习惯把因子随意调换。

## 3. 转置、单位矩阵与逆矩阵

### 转置的T：把第几行变成第几列

上标 $\mathsf T$ 表示**转置**，与第四节的“秩rank”是不同概念。转置把行、列互换：若A是2×3，$A^{\mathsf T}$ 就是3×2；$(A^{\mathsf T})_{ij}=a_{ji}$。

$$\begin{pmatrix}1&2&3\\4&5&6\end{pmatrix}^{\mathsf T}=\begin{pmatrix}1&4\\2&5\\3&6\end{pmatrix}$$

原第一行1、2、3变成第一列；第二行4、5、6变成第二列。原来的第2行第3列元素6，转置后位于第3行第2列，值没有改变。

### 转置有哪些规则？先列条件，再用数字验证

| 规则 | 条件与含义 |
| --- | --- |
| $(A^{\mathsf T})^{\mathsf T}=A$ | 行列交换两次，回到原矩阵 |
| $(A+B)^{\mathsf T}=A^{\mathsf T}+B^{\mathsf T}$ | A、B同形状；加法转置保持相加顺序 |
| $(A-B)^{\mathsf T}=A^{\mathsf T}-B^{\mathsf T}$ | A、B同形状；减号和顺序保留 |
| $(cA)^{\mathsf T}=cA^{\mathsf T}$ | c是标量；数乘可移到转置外 |
| $(AB)^{\mathsf T}=B^{\mathsf T}A^{\mathsf T}$ | AB维度合法；乘积转置必须反转因子顺序 |

**① 加法转置为什么成立？**

下面另取一组便于手算的2×2矩阵：

$$P=\begin{pmatrix}1&2\\3&4\end{pmatrix},\qquad Q=\begin{pmatrix}0&1\\2&3\end{pmatrix}$$

先相加再转置：

$$P+Q=\begin{pmatrix}1&3\\5&7\end{pmatrix},\qquad (P+Q)^{\mathsf T}=\begin{pmatrix}1&5\\3&7\end{pmatrix}$$

先分别转置再相加：

$$P^{\mathsf T}+Q^{\mathsf T}=\begin{pmatrix}1&3\\2&4\end{pmatrix}+\begin{pmatrix}0&2\\1&3\end{pmatrix}=\begin{pmatrix}1&5\\3&7\end{pmatrix}$$

两种路径得到相同矩阵。这也能逐元素理解：原来第i行第j列相加的两项，一起移到了第j行第i列，相加关系没有改变。因此第2-03题的C选项成立。

**② 乘积转置为什么要反过来？**

仍使用刚给出的P、Q。先相乘再转置：

$$PQ=\begin{pmatrix}4&7\\8&15\end{pmatrix},\qquad (PQ)^{\mathsf T}=\begin{pmatrix}4&8\\7&15\end{pmatrix}$$

把因子转置，**反过来**相乘：

$$Q^{\mathsf T}P^{\mathsf T}=\begin{pmatrix}0&2\\1&3\end{pmatrix}\begin{pmatrix}1&3\\2&4\end{pmatrix}=\begin{pmatrix}4&8\\7&15\end{pmatrix}$$

如果不反转顺序，则：

$$P^{\mathsf T}Q^{\mathsf T}=\begin{pmatrix}1&3\\2&4\end{pmatrix}\begin{pmatrix}0&2\\1&3\end{pmatrix}=\begin{pmatrix}3&11\\4&16\end{pmatrix}$$

这个结果与 $(PQ)^{\mathsf T}$ 不同，因此不能写成原顺序的 $P^{\mathsf T}Q^{\mathsf T}$。

从元素公式看，AB的第j行第i列为 $\sum_k a_{jk}b_{ki}$。转置后它成为第i行第j列；而 $B^{\mathsf T}A^{\mathsf T}$ 的对应元素是 $\sum_k b_{ki}a_{jk}$，是同一组数的乘积之和。这解释了反转顺序的来源。

形状也可排错：A为2×3、B为3×4，AB转置为4×2；右边 $B^{\mathsf T}A^{\mathsf T}$ 是4×3乘3×2，也为4×2。但**形状相同只是必要检查，不等于数值已被证明相同**，方阵时错误写法也可能形状合法。

**③ 连续多个因子转置。**

$$ (ABC)^{\mathsf T}=C^{\mathsf T}B^{\mathsf T}A^{\mathsf T} $$

可以先把AB看成一个整体：$(ABC)^{\mathsf T}=C^{\mathsf T}(AB)^{\mathsf T}$，再展开乘积转置，得到上式。结合律允许调整括号；乘积转置要求反转顺序，这两个规则要分清。

### 单位矩阵：矩阵乘法中的“1”

单位矩阵 $I_n$ 是n×n，**主对角线**即左上到右下的位置全为1，其余位置全为0：

$$I_2=\begin{pmatrix}1&0\\0&1\end{pmatrix},\qquad I_3=\begin{pmatrix}1&0&0\\0&1&0\\0&0&1\end{pmatrix}$$

例如用刚才的P：

$$PI_2=\begin{pmatrix}1\times1+2\times0&1\times0+2\times1\\3\times1+4\times0&3\times0+4\times1\end{pmatrix}=\begin{pmatrix}1&2\\3&4\end{pmatrix}=P$$

左乘也有 $I_2P=P$。一般A为m×n时，$I_mA=A$、$AI_n=A$，单位矩阵大小要匹配。它不是“所有元素都是1”的矩阵。

### 逆矩阵：怎样撤销A的变换

对n×n方阵A，如果存在矩阵 $A^{-1}$ 满足：

$$AA^{-1}=A^{-1}A=I_n$$

就称它为A的逆矩阵。上标−1表示“逆”，并非减去1，也不是每个元素分别取倒数。不是所有方阵都有逆；非方阵的左逆、右逆和伪逆需要另外定义，本节先学通常的双侧逆。

**方法一：2×2矩阵直接用公式。**

给定：

$$A=\begin{pmatrix}a&b\\c&d\end{pmatrix}$$

先算 $\Delta=ad-bc$，这个数就是A的行列式 $\det(A)$，第6节会再讲它的性质。若 $\Delta=0$，A不可逆；若 $\Delta\ne0$：

$$A^{-1}=\frac{1}{ad-bc}\begin{pmatrix}d&-b\\-c&a\end{pmatrix}$$

按四步做：①算ad−bc；②交换主对角线的a与d；③把另外两项b、c变号；④每项除以ad−bc。**这个简式只针对2×2矩阵。**

**完整例子：求 $M=\begin{pmatrix}1&2\\3&4\end{pmatrix}$ 的逆。**

第1步，a=1、b=2、c=3、d=4，算行列式：

$$\Delta=1\times4-2\times3=-2\ne0$$

第2步交换对角线的1与4，第3步把2与3变号，得到 $\begin{pmatrix}4&-2\\-3&1\end{pmatrix}$。

第4步每项除以−2：

$$M^{-1}=\frac{1}{-2}\begin{pmatrix}4&-2\\-3&1\end{pmatrix}=\begin{pmatrix}-2&1\\\frac32&-\frac12\end{pmatrix}$$

**算完要验：乘回去是否得到单位矩阵？**

$$MM^{-1}=\begin{pmatrix}1&2\\3&4\end{pmatrix}\begin{pmatrix}-2&1\\\frac32&-\frac12\end{pmatrix}=\begin{pmatrix}-2+3&1-1\\-6+6&3-2\end{pmatrix}=\begin{pmatrix}1&0\\0&1\end{pmatrix}$$

也可以检查另一侧 $M^{-1}M=I_2$。例如逆矩阵第一行乘M第二列为 $(-2)\times2+1\times4=0$，符合单位矩阵非对角线为0。

**反例：什么时候没有逆？**

$$N=\begin{pmatrix}1&2\\2&4\end{pmatrix},\qquad \det(N)=1\times4-2\times2=0$$

此时不能除以0，N不可逆。它把不同输入 $(0,0)^{\mathsf T}$ 和 $(-2,1)^{\mathsf T}$ 都映成零向量，无法由输出唯一恢复输入。

### 方法二：用初等行变换求逆

对方阵，把A和同大小的单位矩阵并排，写成增广矩阵 $[A\mid I]$。对**整行**做相同变换，如果左边能化成I，右边就变成 $A^{-1}$：

$$[A\mid I]\longrightarrow[I\mid A^{-1}]$$

允许的初等行变换有三种：交换两行；一行乘非零常数；把某行的倍数加到另一行。竖线只是左右分隔，不是行列式符号。左右两块必须一起变，不能只改左边。

继续使用上面的M。先写：

$$\left[\begin{array}{cc|cc}1&2&1&0\\3&4&0&1\end{array}\right]$$

记 $R_1$、$R_2$ 为第1行、第2行。先做 $R_2\leftarrow R_2-3R_1$：

$$\left[\begin{array}{cc|cc}1&2&1&0\\0&-2&-3&1\end{array}\right]$$

再做 $R_2\leftarrow-\frac12R_2$：

$$\left[\begin{array}{cc|cc}1&2&1&0\\0&1&\frac32&-\frac12\end{array}\right]$$

最后做 $R_1\leftarrow R_1-2R_2$：

$$\left[\begin{array}{cc|cc}1&0&-2&1\\0&1&\frac32&-\frac12\end{array}\right]$$

左边成为 $I_2$，右边为 $\begin{pmatrix}-2&1\\\frac32&-\frac12\end{pmatrix}$，与公式法得到的逆相同。这个思路也可用于更大的方阵；若左边无法化成单位矩阵，就没有通常的逆。

为什么右边是逆？整串行变换等价于左乘同一个变换E，左块变为EA，右块由I变为E。当EA=I时，对这里的方阵，E就是 $A^{-1}$。

### 逆矩阵的用途与常考规则

如果 $M\mathbf x=\mathbf y$ 且M可逆，就可左乘逆矩阵，得到 $\mathbf x=M^{-1}\mathbf y$。例如 $\mathbf y=(5,11)^{\mathsf T}$：

$$\mathbf x=\begin{pmatrix}-2&1\\\frac32&-\frac12\end{pmatrix}\begin{pmatrix}5\\11\end{pmatrix}=\begin{pmatrix}-10+11\\\frac{15}{2}-\frac{11}{2}\end{pmatrix}=\begin{pmatrix}1\\2\end{pmatrix}$$

把x代回M即可验证输出为(5,11)。逆矩阵的作用正是把输出恢复到对应输入。

对可逆的同阶方阵A、B：

$$ (AB)^{-1}=B^{-1}A^{-1},\qquad (A^{-1})^{-1}=A,\qquad (A^{\mathsf T})^{-1}=(A^{-1})^{\mathsf T} $$

第一条也反转顺序：$(AB)(B^{-1}A^{-1})=A(BB^{-1})A^{-1}=I$，中间只是用结合律改括号，并没有交换A、B的位置。转置和求逆虽有一些相似规则，但操作本身不同。

本节练习前先自查：加法转置是否反转顺序？乘积转置是否反转？2×2求逆第一步算什么？答案依次是“不需要”“需要”“先算ad−bc是否为0”。

## 4. 线性方程、初等行变换、秩与零空间

这一节按“看懂方程→学会行变换→计算秩→求全部解→理解零空间”的顺序进行。主要使用同一个矩阵，避免在定义之间跳跃。

### ① A乘x是什么意思？先展开成两条方程

给定系数矩阵A，以及包含两个未知数的列向量x：

$$A=\begin{pmatrix}1&2\\2&4\end{pmatrix},\qquad \mathbf x=\begin{pmatrix}x_1\\x_2\end{pmatrix}$$

A中的1、2、2、4是已知系数，$x_1,x_2$ 是要求的未知数。按上一节的矩阵乘法：

$$A\mathbf x=\begin{pmatrix}1\times x_1+2\times x_2\\2\times x_1+4\times x_2\end{pmatrix}=\begin{pmatrix}x_1+2x_2\\2x_1+4x_2\end{pmatrix}$$

因此，一个矩阵等式 $A\mathbf x=\mathbf b$ 表示**左侧输出向量的每个分量，分别等于右侧对应分量**。若 $\mathbf b=(b_1,b_2)^{\mathsf T}$，它就是：

$$\begin{cases}x_1+2x_2=b_1\\2x_1+4x_2=b_2\end{cases}$$

矩阵的每一行对应一条方程，每一列对应一个未知数的系数。一般A为m×n，就有m条方程、n个未知数；x是n维列向量，b是m维列向量。

### ② 右边的粗体0是什么？零解又是什么？

在 $A\mathbf x=\mathbf0$ 中，$\mathbf0$ 是**零向量**。本例输出有两个分量，所以右边为 $(0,0)^{\mathsf T}$，并非只要求两个输出相加等于0。

$$\begin{pmatrix}1&2\\2&4\end{pmatrix}\begin{pmatrix}x_1\\x_2\end{pmatrix}=\begin{pmatrix}0\\0\end{pmatrix}
\quad\Longleftrightarrow\quad
\begin{cases}x_1+2x_2=0\\2x_1+4x_2=0\end{cases}$$

这种右端全为0的线性方程组，叫**齐次线性方程组**。这里“齐次”先理解为右边是零向量即可。

取 $x_1=0,x_2=0$，两个方程都成立。因此**齐次线性方程组一定有零解**。零解是指未知向量x全部为0；这不要求系数矩阵A本身为零。

**非零解**指x至少一个分量不为0，不要求每个分量都非零。本例取 $x_1=-2,x_2=1$：

$$A\begin{pmatrix}-2\\1\end{pmatrix}=\begin{pmatrix}-2+2\\-4+4\end{pmatrix}=\begin{pmatrix}0\\0\end{pmatrix}$$

所以本例还有非零解。输入非零而输出为零，是因为各项相互抵消。

但并非所有A都有非零解：若A是单位矩阵 $I_2$，则 $I_2\mathbf x=\mathbf x$，要求输出为零就只能令x为零。

### ③ 初等行变换是什么？只允许三种可逆操作

**初等行变换是按规定改变矩阵整行的操作。** 记 $R_1$ 为第一行、$R_2$ 为第二行。它用来简化矩阵，帮助解方程、计算秩或求逆。

下面三个示范**各自从原矩阵A开始**，不是前后连续的步骤。

**操作一：交换两行。**

$$\begin{pmatrix}1&2\\2&4\end{pmatrix}
\xrightarrow{R_1\leftrightarrow R_2}
\begin{pmatrix}2&4\\1&2\end{pmatrix}$$

在方程组里，相当于把两条方程换个排列顺序。交换回来就能恢复。

**操作二：一整行乘同一个非零常数。** 例如第一行乘3：

$$\begin{pmatrix}1&2\\2&4\end{pmatrix}
\xrightarrow{R_1\leftarrow3R_1}
\begin{pmatrix}3&6\\2&4\end{pmatrix}$$

这一行的每个元素都乘3，不能只改其中一个。非零倍数可通过除回去恢复；乘0则可能抹掉一条方程的信息，不是允许的这种初等行变换。

**操作三：把另一行的倍数加到某一行。** 例如第二行减去第一行的2倍：

$$R_2\leftarrow R_2-2R_1,\qquad (2,4)-2(1,2)=(0,0)$$

所以：

$$\begin{pmatrix}1&2\\2&4\end{pmatrix}
\xrightarrow{R_2\leftarrow R_2-2R_1}
\begin{pmatrix}1&2\\0&0\end{pmatrix}$$

箭头 $\leftarrow$ 表示“把左边那一行替换成右边计算出的行”。第一行不变，只替换第二行；操作后可把第一行的2倍加回第二行，恢复原矩阵。

**为什么解方程时可以这样做？**

本例第二条方程减去第一条的2倍：

$$ (2x_1+4x_2)-2(x_1+2x_2)=0-2\times0 $$

化简为 $0=0$。原来第二条就是第一条的重复信息，化简后仍保留同样的全部解。

对一般 $A\mathbf x=\mathbf b$，必须连同右侧b一起变换。通常写成增广矩阵 $[A\mid\mathbf b]$，对**包括右侧在内的整行**操作。这些可逆操作保持方程组的解集；只改左边而不改右边，会变成另一个问题。

### ④ 阶梯形和主元：为什么化简后才数非零行？

**行阶梯形**像逐级向右的台阶，主要要求：

1. 全零行放在所有非零行的下方。
2. 每个非零行从左边数的第一个非零元素，称该行的**主元**；下方行的主元要比上方行更靠右。

因此每个主元下方都为0。计算秩时不要求主元一定等于1；把主元化为1、再清除其上方元素，是进一步化简。

例如下列矩阵已经是行阶梯形：

$$H=\begin{pmatrix}1&2&3\\0&5&6\\0&0&0\end{pmatrix}$$

第一行主元在第1列，第二行主元在第2列，共2个主元、2条非零行。

但 $\begin{pmatrix}1&2\\2&4\end{pmatrix}$ 不是阶梯形：两行的第一个非零元素都在第1列，而且第二行重复第一行的信息。不能直接数两条非零行，就说秩为2。

### ⑤ 线性组合、相关、无关：什么叫“重复信息”？

**线性组合**是给向量分别乘标量，再相加。例如 $\alpha\mathbf u+\beta\mathbf v$，alpha、beta是可选择的系数。

若 $\mathbf u=(1,2)^{\mathsf T}$、$\mathbf v=(2,4)^{\mathsf T}=2\mathbf u$，那么：

$$\alpha\mathbf u+\beta\mathbf v=(\alpha+2\beta)\mathbf u$$

无论怎样选择两个系数，结果仍沿着u所在的同一条直线，没有产生第二个独立方向。

更一般地，如果能找到**不全为0**的系数，让若干向量的线性组合为零向量，这些向量就**线性相关**。例如：

$$2\mathbf u-\mathbf v=\mathbf0$$

系数2和−1不全为0，所以u、v相关。反之，如果只有把所有系数都设为0才能组合成零向量，就称这些向量**线性无关**。

例如 $\mathbf e_1=(1,0)^{\mathsf T}$、$\mathbf e_2=(0,1)^{\mathsf T}$：

$$\alpha\mathbf e_1+\beta\mathbf e_2=\begin{pmatrix}\alpha\\\beta\end{pmatrix}=\mathbf0
\quad\Longrightarrow\quad \alpha=\beta=0$$

它们线性无关，提供两个独立方向。向量个数多，不代表独立方向也一定多。

### ⑥ 秩：独立方向的数量，怎样实际算出来？

矩阵的**秩** $\operatorname{rank}(A)$ 是最多能选出多少条线性无关的列，也等于最多能选出多少条线性无关的行。行秩与列秩相等，这个共同的数就叫秩。

本例A的两列为 $(1,2)^{\mathsf T}$、$(2,4)^{\mathsf T}$，第二列是第一列的2倍，只有一个独立方向，所以秩为1。

计算时也可用初等行变换化成阶梯形，数主元或非零行。初等行变换不改变秩：

$$A=\begin{pmatrix}1&2\\2&4\end{pmatrix}
\xrightarrow{R_2\leftarrow R_2-2R_1}
\begin{pmatrix}1&2\\0&0\end{pmatrix}
\quad\Longrightarrow\quad \operatorname{rank}(A)=1$$

这里化简后只有一个主元。**秩不是非零元素个数，也不能对任意未化简矩阵直接数非零行。**

一般A有m行n列，独立行最多m条、独立列最多n条，因此：

$$0\le\operatorname{rank}(A)\le\min(m,n),\qquad A\in\mathbb R^{m\times n}$$

例如3×5矩阵秩最多3；零矩阵秩为0；$I_2$ 的两列无关，秩为2。前面的H为阶梯形，有两个主元，所以秩为2。

### ⑦ 回到Ax=0：怎样求出全部解？

对本例做刚才的行变换后：

$$\begin{cases}x_1+2x_2=0\\0=0\end{cases}$$

第二行对未知数不再增加限制，因此只需满足 $x_1=-2x_2$。这仍有两个未知数，只留下一条独立约束。

可以**自由选择** $x_2$，例如0、1、−1、2或其他实数；然后 $x_1$ 必须取−2倍的值。把自由选择的数记为t：

$$x_2=t,\qquad x_1=-2t,\qquad \mathbf x=\begin{pmatrix}-2t\\t\end{pmatrix}=t\begin{pmatrix}-2\\1\end{pmatrix},\quad t\in\mathbb R$$

| 自由选择的t | 得到的未知向量x | 代入第一条方程 |
| --- | --- | --- |
| 0 | $(0,0)^{\mathsf T}$ | $0+2\times0=0$ |
| 1 | $(-2,1)^{\mathsf T}$ | $-2+2\times1=0$ |
| −1 | $(2,-1)^{\mathsf T}$ | $2+2\times(-1)=0$ |
| 2 | $(-4,2)^{\mathsf T}$ | $-4+2\times2=0$ |

这些只是解的几个例子。t可以取任意实数，所以共有无穷多个解。**x是整个未知向量，t是描述所有解的一个自由参数**，两者不要混为一谈。

### ⑧ 零空间：把所有满足Ax=0的向量收集起来

零空间记为 $\ker(A)$ 或 $\operatorname{Null}(A)$：

$$\ker(A)=\{\mathbf x\in\mathbb R^n:A\mathbf x=\mathbf0\}$$

花括号表示一个集合：把所有经A变换后输出为零向量的输入x放进去。零空间包含的是**输入向量**，不是矩阵A中“值为0的那些位置”，也不只是零向量本身。

因为已经求出了本例的全部解，所以现在可以写：

$$\ker(A)=\left\{t\begin{pmatrix}-2\\1\end{pmatrix}:t\in\mathbb R\right\}$$

它是一条经过原点的直线，由一个非零方向向量 $(-2,1)^{\mathsf T}$ 生成。这个向量可以作为零空间的一组**基**：一组线性无关、又能线性组合出空间内全部向量的向量。

本例一组基只需一个向量，所以**零空间维数为1**。虽然每个x都写成两个分量，实际只需选一个自由参数t；“向量有两个分量”和“解空间维数为1”并不矛盾。

若A是 $I_2$，零空间只有零向量，维数为0。维数0不表示集合为空，零向量仍在其中。

### ⑨ 最后再理解秩—零度公式

对m×n矩阵，x有n个未知分量。行化简后，每个主元约束一个主元变量，其余是自由变量：

$$\operatorname{rank}(A)+\dim\ker(A)=n$$

- $\operatorname{rank}(A)$：主元数量，即独立约束／独立方向数。
- $\dim\ker(A)$：零空间维数，即齐次方程的自由变量数量。
- n：A的**列数**，也就是未知数个数，不是行数。

本例n=2、秩=1，有一个自由变量，因此 $1+1=2$。A为3×5且秩为3时，齐次方程有 $5-3=2$ 个自由变量，零空间维数2；从公式知道维数，不代表已经算出了具体的基。

自查：Ax=0中的0是什么？齐次方程会无解吗？本例为什么不是两个自由变量？答案是“输出零向量”“不会，至少有零解”“一条独立方程约束了两个未知数中的一个自由度”。

## 5. 方程有解、唯一解、无穷多解

这一节把上一节的右端零向量换成给定目标b。仍先问“能否满足所有方程”，再问“若能满足，有几个解”。

### ① 同一个A，换目标b后可能有解，也可能无解

继续使用：

$$A=\begin{pmatrix}1&2\\2&4\end{pmatrix}$$

**情况一：目标为 $\mathbf b=(3,6)^{\mathsf T}$。**

$$A\mathbf x=\mathbf b
\quad\Longleftrightarrow\quad
\begin{cases}x_1+2x_2=3\\2x_1+4x_2=6\end{cases}$$

把右端接到系数矩阵右边，形成增广矩阵。仍做第二行减第一行的2倍，右端一起计算：

$$\left[\begin{array}{cc|c}1&2&3\\2&4&6\end{array}\right]
\xrightarrow{R_2\leftarrow R_2-2R_1}
\left[\begin{array}{cc|c}1&2&3\\0&0&0\end{array}\right]$$

第二行变成0=0，没有矛盾。令 $x_2=t$，第一行给出 $x_1=3-2t$：

$$\mathbf x=\begin{pmatrix}3-2t\\t\end{pmatrix},\qquad t\in\mathbb R$$

t=0时解是(3,0)，t=1时解是(1,1)。两个都能代入得到输出(3,6)，而且t还能取其他实数，因此有**无穷多解**。

**情况二：目标改为 $\mathbf b=(3,7)^{\mathsf T}$。**

$$\left[\begin{array}{cc|c}1&2&3\\2&4&7\end{array}\right]
\xrightarrow{R_2\leftarrow R_2-2R_1}
\left[\begin{array}{cc|c}1&2&3\\0&0&1\end{array}\right]$$

第二行表示 $0x_1+0x_2=1$，即0=1，不可能成立，所以**无解**。也可直接看：左边第二条方程始终是第一条左边的2倍，右边也必须是2倍；3和7不满足这个要求。

可见A不变时，不同b的可解性也可能不同。齐次方程b=0一定有零解，一般非齐次方程则可能无解。

### ② 唯一解怎样算出来？

另取系数矩阵 $M=\begin{pmatrix}1&2\\3&4\end{pmatrix}$，目标 $(5,11)^{\mathsf T}$：

$$\left[\begin{array}{cc|c}1&2&5\\3&4&11\end{array}\right]
\xrightarrow{R_2\leftarrow R_2-3R_1}
\left[\begin{array}{cc|c}1&2&5\\0&-2&-4\end{array}\right]$$

从第二行先得到 $-2x_2=-4$，所以 $x_2=2$。代回第一行 $x_1+2\times2=5$，得到 $x_1=1$。每个未知数都被确定，没有可自由选择的参数，所以解唯一。

第3节用逆矩阵算出的也是这个解。**消元与求逆是不同解题方法，得到的解应一致。**

### ③ 列空间：A能产生哪些输出？

把A的各列记为 $\mathbf a_1,\ldots,\mathbf a_n$，矩阵乘法也可看成：

$$A\mathbf x=x_1\mathbf a_1+\cdots+x_n\mathbf a_n$$

每个未知数是对应列的组合系数。**列空间** $\operatorname{Col}(A)$ 就是A各列能组合出的全部向量，也是A能产生的全部输出。其维数为 $\operatorname{rank}(A)$。

本节开头A的两列为 $(1,2)^{\mathsf T}$、$(2,4)^{\mathsf T}$：

$$A\mathbf x=(x_1+2x_2)\begin{pmatrix}1\\2\end{pmatrix}$$

所以输出总是形如 $(s,2s)^{\mathsf T}$ 的向量。(3,6)在这条直线上，能够得到；(3,7)不在，无法得到。这就是“b在列空间内，当且仅当Ax=b有解”的含义。

### ④ 用秩判断有解、唯一解与无穷多解

记r为系数矩阵A的秩，n为未知数个数，即A的列数。增广矩阵 $[A\mid\mathbf b]$ 把b接为额外一列，秩也要单独计算。

| 条件 | 结论 | 消元时会看到什么 |
| --- | --- | --- |
| $\operatorname{rank}(A)<\operatorname{rank}([A\mid\mathbf b])$ | 无解 | 系数全0、右端非0的矛盾行 |
| $\operatorname{rank}(A)=\operatorname{rank}([A\mid\mathbf b])=n$ | 唯一解 | 有解，且没有自由变量 |
| $\operatorname{rank}(A)=\operatorname{rank}([A\mid\mathbf b])<n$ | 无穷多解 | 有解，并有n−r个自由变量 |

这些结论针对本讲义的实数线性方程组。**先确认有解，再用n−r讨论解的自由度；不能给无解的方程组也数出“一族解”。**

前面两个使用A的例子，A的秩都是1。目标(3,6)时，增广矩阵化简后也只有一个主元，秩为1，小于n=2，所以无穷多解；目标(3,7)时，增广矩阵在右端列又出现一个主元，秩为2，大于A的秩1，所以无解。

### ⑤ 一个特解加上齐次解，为什么仍是解？

设 $\mathbf x_0$ 是Ax=b的一个已知解，称**特解**；z是对应齐次方程Az=0的任意解。则：

$$A(\mathbf x_0+\mathbf z)=A\mathbf x_0+A\mathbf z=\mathbf b+\mathbf0=\mathbf b$$

因此“特解＋任意齐次解”仍是原方程的解。反过来，任何其他解减去这个特解，都会落入零空间。所以**全部解**可以写成：

$$\mathbf x=\mathbf x_0+\mathbf z,\qquad \mathbf z\in\ker(A)$$

本例目标(3,6)时，可以选特解 $\mathbf x_0=(3,0)^{\mathsf T}$；上一节已经求出齐次解 $\mathbf z=t(-2,1)^{\mathsf T}$：

$$\mathbf x=\begin{pmatrix}3\\0\end{pmatrix}+t\begin{pmatrix}-2\\1\end{pmatrix}=\begin{pmatrix}3-2t\\t\end{pmatrix}$$

如果零空间里只有零向量，就不能从特解出发加出不同解，因此有解时唯一；如果零空间里有非零方向，就能沿它得到无穷多个解。

### ⑥ 满行秩与满列秩：两个保证分别是什么？

**满行秩**表示 $\operatorname{rank}(A)=m$，即秩达到行数。列空间于是覆盖整个m维输出空间，因此**任意m维b都有解**；是否唯一还要看列数n。

例如 $A=\begin{pmatrix}1&0&0\\0&1&0\end{pmatrix}$ 为2×3，秩为2，满行秩。对任意目标 $(b_1,b_2)^{\mathsf T}$：

$$\mathbf x=\begin{pmatrix}b_1\\b_2\\t\end{pmatrix},\qquad t\in\mathbb R$$

都能满足Ax=b。第三个未知数自由，说明“任意b有解”不等于“唯一解”。

**满列秩**表示 $\operatorname{rank}(A)=n$，即秩达到列数。此时齐次方程没有自由变量，所以**对给定b，如果有解就唯一**；它并不保证任意b都有解。

例如 $A=\begin{pmatrix}1&0\\0&1\\0&0\end{pmatrix}$ 为3×2，秩为2，满列秩。方程要求 $x_1=b_1$、$x_2=b_2$、$0=b_3$。b第三个分量为0时有唯一解，第三个分量非0时无解。

| 条件 | 对一般Ax=b能保证什么 |
| --- | --- |
| 满行秩：rank(A)=m | 任意m维b都有解；n大于m时解不唯一 |
| 满列秩：rank(A)=n | 对给定b若有解就唯一；m大于n时不是任意b都有解 |
| 方阵满秩：m=n=rank(A) | 任意b都有唯一解，A可逆 |

**再做题目中的3×5例子。** A有3行5列，秩为3，满行秩，因此任意三维b都有解。有5个未知数、3个主元，剩 $5-3=2$ 个自由变量，所以每个b都有无穷多解。

自查：系数行全0、右端为1说明什么？“满列秩”能否直接推出任意b都有解？答案是“无解”“不能，保证的是有解时唯一”。

## 6. 行列式、特征值与正定的入门判断

### ① 先保留行列式这把工具

行列式 $\det(A)$ 只对方阵定义。2×2的公式：

$$\det\begin{pmatrix}a&b\\c&d\end{pmatrix}=ad-bc$$

例如 $\det\begin{pmatrix}1&2\\3&4\end{pmatrix}=4-6=-2$，不为0，因此可逆。两行成比例时行列式为0；三角矩阵的行列式等于对角线乘积。交换两行，行列式变号。

### ② 特征向量是什么？把矩阵看作一次变换

前面已经讲过：矩阵乘向量 $A\mathbf v$，可以看成把输入向量变成一个新向量。一般情况下，向量的长度和方向都可能变化。

但有些**特殊的非零向量**，变换后的结果恰好是它自身的某个数倍。这些向量叫A的**特征向量**，对应的倍数叫**特征值**：

$$A\mathbf v=\lambda\mathbf v,\qquad\mathbf v\ne\mathbf0$$

| 符号 | 在这里的意思 |
| --- | --- |
| $A$ | 一个给定的n×n方阵，表示这次线性变换 |
| $\mathbf v$ | 我们要找的n维非零向量，即特征向量 |
| $A\mathbf v$ | 向量经过A变换后的结果 |
| $\lambda$ | 一个数，读作lambda；表示结果是原向量的多少倍 |

**左边是“先用矩阵变换”，右边是“直接给原向量乘一个数”；两边得到同一个向量。** 特征值与特征向量是一对对应关系，不能把一个特征值和任意向量随意配对。

当 $\lambda>0$，结果同方向；当 $\lambda<0$，结果反方向。例如 $\lambda=-2$ 表示反向且长度变成2倍。长度的倍数是 $|\lambda|$，不是可能为负的lambda本身。当 $\lambda=0$，原来的非零向量被压成零向量；零向量没有方向，所以这时不能说“仍保持方向”。

为什么要求 $\mathbf v\ne\mathbf0$？因为 $A\mathbf0=\lambda\mathbf0=\mathbf0$ 对任何lambda都成立，零向量无法挑出这次变换的特殊倍数。**特征向量不能为零，但特征值可以为零。**

### ③ 先验算：为什么diag(2,3)的特征值是2和3？

$\operatorname{diag}(2,3)$ 是下面这个对角矩阵的简写。取两个坐标轴方向的向量：

$$D=\begin{pmatrix}2&0\\0&3\end{pmatrix},\quad\mathbf e_1=\begin{pmatrix}1\\0\end{pmatrix},\quad\mathbf e_2=\begin{pmatrix}0\\1\end{pmatrix}$$

分别按“一行对一列”计算：

$$D\mathbf e_1=\begin{pmatrix}2\times1+0\times0\\0\times1+3\times0\end{pmatrix}=\begin{pmatrix}2\\0\end{pmatrix}=2\mathbf e_1$$

$$D\mathbf e_2=\begin{pmatrix}2\times0+0\times1\\0\times0+3\times1\end{pmatrix}=\begin{pmatrix}0\\3\end{pmatrix}=3\mathbf e_2$$

因此，$\mathbf e_1$ 对应特征值2，$\mathbf e_2$ 对应特征值3。横轴方向放大2倍，纵轴方向放大3倍。

但并非每个向量都是D的特征向量。例如 $\mathbf w=(1,1)^{\mathsf T}$：

$$D\mathbf w=\begin{pmatrix}2\\3\end{pmatrix}$$

如果它等于 $\lambda(1,1)^{\mathsf T}$，第一个分量要求lambda=2，第二个分量又要求lambda=3，不可能由**同一个数**同时满足，所以w不是特征向量。

如果v是对应lambda的特征向量，任何非零倍数 $c\mathbf v$ 也对应同一个lambda，因为 $A(c\mathbf v)=cA\mathbf v=\lambda(c\mathbf v)$。因此特征向量通常不唯一；写出一个方向代表即可，只有要求单位向量时才需要把长度变为1。

### ④ 怎样求特征值？从Av=lambda v到一个普通方程

前面是在“给定向量后验证”。如果只给A，要怎样主动找出lambda和v？

把 $A\mathbf v=\lambda\mathbf v$ 移项。注意A是矩阵，lambda是数，要先把它写成同阶矩阵 $\lambda I$ 才能相减：

$$A\mathbf v-\lambda I\mathbf v=\mathbf0\quad\Longrightarrow\quad(A-\lambda I)\mathbf v=\mathbf0$$

这与第4节的齐次方程相连：我们需要v是**非零解**。对于方阵，齐次方程有非零解，等价于系数矩阵不可逆，也等价于它的行列式为0。所以：

$$\det(A-\lambda I)=0$$

这叫**特征方程**。先解它得到特征值，再对每个特征值解 $(A-\lambda I)\mathbf v=\mathbf0$，得到对应的非零特征向量。不是让 $\det(A)=0$；变成0的是 $A-\lambda I$ 的行列式。

### ⑤ 完整例子：先求特征值，再求对应向量

给定一个不是对角矩阵的例子：

$$A=\begin{pmatrix}2&1\\1&2\end{pmatrix}$$

**第一步：写出A−lambda I。** lambda只从主对角线减去，其他位置不变：

$$A-\lambda I=\begin{pmatrix}2-\lambda&1\\1&2-\lambda\end{pmatrix}$$

**第二步：算行列式并解方程。**

$$\det(A-\lambda I)=(2-\lambda)^2-1=\lambda^2-4\lambda+3=(\lambda-3)(\lambda-1)=0$$

所以特征值是 $\lambda_1=3$ 和 $\lambda_2=1$。这里下标只用于区分两个值，并不表示向量分量。

**第三步：对lambda=3求向量。** 把3代回，记未知向量为 $\mathbf v=(x,y)^{\mathsf T}$：

$$\begin{pmatrix}-1&1\\1&-1\end{pmatrix}\begin{pmatrix}x\\y\end{pmatrix}=\begin{pmatrix}0\\0\end{pmatrix}\quad\Longrightarrow\quad -x+y=0,\quad x-y=0$$

两条方程其实都要求 $y=x$。令x=t，则所有解为 $t(1,1)^{\mathsf T}$。特征向量要求非零，因此 **t不能为0**。选最简单的t=1，得到 $\mathbf v_1=(1,1)^{\mathsf T}$。

**第四步：对lambda=1求向量。**

$$\begin{pmatrix}1&1\\1&1\end{pmatrix}\begin{pmatrix}x\\y\end{pmatrix}=\begin{pmatrix}0\\0\end{pmatrix}\quad\Longrightarrow\quad x+y=0$$

所以 $y=-x$，全部特征向量为 $t(1,-1)^{\mathsf T}$，t非零。选t=1，得到 $\mathbf v_2=(1,-1)^{\mathsf T}$。

**第五步：乘回去验证配对。**

$$A\begin{pmatrix}1\\1\end{pmatrix}=\begin{pmatrix}3\\3\end{pmatrix}=3\begin{pmatrix}1\\1\end{pmatrix},\qquad A\begin{pmatrix}1\\-1\end{pmatrix}=\begin{pmatrix}1\\-1\end{pmatrix}=1\begin{pmatrix}1\\-1\end{pmatrix}$$

因此沿 $(1,1)^{\mathsf T}$ 的方向放大3倍，沿 $(1,-1)^{\mathsf T}$ 的方向不变。这说明**特征向量不一定沿坐标轴**。也不能直接把一般矩阵的对角线当特征值：本例对角线是2、2，特征值却是3、1。

### ⑥ 与可逆、迹、行列式有什么关系？

**先背这一张表，再看下面的理由。第2-09题考的就是这组等价条件。**

**前提：A是n×n方阵。** 下表每一行都与“A可逆”等价；知道任意一行成立，就能推出其他所有行成立。“等价”表示可以双向推断，不只是“A可逆时这些成立”。

| 可逆的等价说法 | 翻译成做题时能用的话 |
| --- | --- |
| $\operatorname{rank}(A)=n$ | 方阵满秩，有n个主元，没有自由变量 |
| $\det(A)\ne0$ | 行列式不为0；注意是“不为0”，不是“大于0” |
| $A\mathbf x=\mathbf0$只有零解 | 除了x=0，没有别的输入会被压成零 |
| $\ker(A)=\{\mathbf0\}$，即零空间维数为0 | 只是把上一行换成零空间语言；不是说零空间为空 |
| 0不是A的特征值 | 没有非零特征向量被压成零；不是“至少一个特征值不为0” |
| 对任意 $\mathbf b\in\mathbb R^n$，$A\mathbf x=\mathbf b$有唯一解 | 每个输出都能找到且只能找到一个输入 |
| A的n列线性无关，n行也线性无关 | 没有冗余方向，行、列都达到最大独立数量 |

**记忆句：方阵可逆 ⇔ 满秩 ⇔ 行列式非零 ⇔ 齐次方程只有零解 ⇔ 没有0特征值。** “⇔”读作“当且仅当”，两边可互相推出。

**为什么可逆能推出齐次方程只有零解？** 假设 $A\mathbf x=\mathbf0$，两边左乘逆矩阵：

$$A^{-1}A\mathbf x=A^{-1}\mathbf0\quad\Longrightarrow\quad I\mathbf x=\mathbf0\quad\Longrightarrow\quad\mathbf x=\mathbf0$$

所以不存在其他非零解。这里是证明“任何满足方程的x都只能为0”，不是仅仅把0代入验证一次。**所有齐次方程都有零解；题目中的关键是“只有”。**

**为什么只有零解与秩为n等价？** 第4节讲过，n个未知数的齐次方程有 $n-\operatorname{rank}(A)$ 个自由变量。如果秩为n，自由变量数为0，唯一解就是零解；如果秩小于n，就至少有一个自由变量，可选出非零解。因此：

$$A\mathbf x=\mathbf0\text{只有零解}\quad\Longleftrightarrow\quad n-\operatorname{rank}(A)=0\quad\Longleftrightarrow\quad\operatorname{rank}(A)=n$$

对n×n方阵，n个主元意味着消元后可化成单位矩阵I。三种初等行变换都可逆，所以整串变换也可逆；若这串变换记为E，就有EA=I，从而A可逆。这把“满秩”和“可逆”接起来了。

**为什么满秩与行列式非零等价？** 对方阵消元得到上三角或阶梯形。交换两行会使行列式变号，某行乘非零数使行列式乘该数，某行加另一行的倍数不改变行列式，因此这些操作都不改变“是否为0”。满秩时有n个非零主元，三角矩阵的行列式是它们的乘积，不为0；不满秩时出现零行，行列式为0。因此原矩阵也满足“满秩 ⇔ 行列式非零”。

**为什么没有0特征值也等价？** 如果0是特征值，就存在非零v满足 $A\mathbf v=0\mathbf v=\mathbf0$，这恰好是齐次方程的一个非零解。反过来，任何非零解也正好是对应特征值0的特征向量。因此“没有0特征值”与“齐次方程只有零解”是同一件事的两种说法。

**第2-09题的陷阱：至少一个，与全部，是两个要求。** 用同一个反例检查：

$$B=\begin{pmatrix}1&0\\0&0\end{pmatrix},\qquad B\begin{pmatrix}x_1\\x_2\end{pmatrix}=\begin{pmatrix}x_1\\0\end{pmatrix}$$

它的特征值是1和0，所以“至少一个非零特征值”确实成立。但是秩只有1，行列式为0，而且 $B(0,1)^{\mathsf T}=\mathbf0$，存在非零解；B不可逆。找到一个“该条件成立而A不可逆”的反例，就能否定它是等价条件。

所以本题：**A选项是满秩，B选项是行列式非零，D选项是齐次方程只有零解，三者都选；C选项只排除了“全为0”，没有排除某个特征值仍为0，不能选。**

另一个常见陷阱是“有唯一解”有没有量词。对方阵，一个给定b若有唯一解，也能推出A可逆：否则存在非零z使Az=0，那么已知解x再加z仍是另一解，产生矛盾。但仅说“有解”不够，甚至仅说“对任意b都有解”在非方阵中也不能推出通常的双侧可逆。**先确认方阵，再套本表。**

**下面单独记迹与行列式，不要把它们与可逆条件混淆。** 可逆只要求特征值全不为0，不要求全为正。例如 $\operatorname{diag}(-2,3)$ 可逆，但不是正定矩阵。

**迹** $\operatorname{tr}(A)$ 是主对角线元素之和。它等于全部特征值之和；行列式等于全部特征值之积：

$$\operatorname{tr}(A)=\lambda_1+\cdots+\lambda_n,\qquad\det(A)=\lambda_1\cdots\lambda_n$$

这里按**代数重数**计数，意思是特征方程的根重复几次，就在和与积里算几次。例如单位矩阵 $I_2$ 的特征方程为 $(1-\lambda)^2=0$，特征值1重复两次，所以迹为1+1=2，行列式为1×1=1；不能只算一个1。

对上面的A，直接算得迹2+2=4，行列式2×2−1×1=3；用特征值算也是3+1=4、3×1=3。可以用它们核对，但不要把“特征值之和等于对角线之和”误解成“每个特征值就是一个对角线元素”。

### ⑦ 与正定有什么关系？注意实对称这个条件

对**实对称矩阵**，正定指任意非零 $\mathbf x$ 都满足 $\mathbf x^{\mathsf T}A\mathbf x>0$，等价于全部特征值为正。半正定把大于号改为大于等于。仅对角线全正不能保证正定：

$$A=\begin{pmatrix}1&2\\2&1\end{pmatrix},\quad\mathbf x=\begin{pmatrix}1\\-1\end{pmatrix},\quad\mathbf x^{\mathsf T}A\mathbf x=-2$$

这个反例中，$A(1,-1)^{\mathsf T}=(-1,1)^{\mathsf T}=-1(1,-1)^{\mathsf T}$，所以−1是特征值。沿这个方向，二次型为负，因而不正定。

为什么特征值会影响二次型？若v对应实特征值lambda，就有：

$$\mathbf v^{\mathsf T}A\mathbf v=\mathbf v^{\mathsf T}(\lambda\mathbf v)=\lambda\,\mathbf v^{\mathsf T}\mathbf v$$

因为v非零，$\mathbf v^{\mathsf T}\mathbf v$ 是各分量平方之和，严格大于0，所以这条方向上二次型的正负与lambda一致。对**实对称矩阵**，还可以选出一组正交的特征向量作为基，任意向量都能沿这些方向分解，因此全部特征值为正能够保证所有非零方向的二次型都为正。一般非对称矩阵不能直接套用这个充分条件。

| 实对称矩阵的特征值情况 | 结论 | 例子 |
| --- | --- | --- |
| 全部大于0 | 正定，且可逆 | 上面的A，特征值3、1 |
| 全部大于等于0，至少一个为0 | 半正定、不正定，且不可逆 | $\operatorname{diag}(1,0)$ |
| 同时有正值和负值 | 不定；若没有0仍可逆 | $\begin{pmatrix}1&2\\2&1\end{pmatrix}$，特征值3、−1 |

协方差矩阵是半正定，可能含0特征值，因此可能不可逆。

### ⑧ 做题时按这个顺序检查

给了A、lambda和v，就先确认v非零，再乘出Av，检查它是否等于**同一个lambda乘整个v**。只给A且要求计算，就先解 $\det(A-\lambda I)=0$，再逐个解向量，最后乘回验证。

两个自查：上面的A与 $\mathbf v=(2,2)^{\mathsf T}$ 对应哪个特征值？$\operatorname{diag}(1,0)$ 的 $(0,1)^{\mathsf T}$ 是不是特征向量？答案分别是3；是，对应特征值0，它本身仍是非零向量。

补充边界：实矩阵不一定有实特征值。例如二维旋转90度没有非零实向量能与旋转前共线，但在复数范围内有特征值。上面的迹和行列式关系可以把复特征值一并计入；本节手算例子均有实特征值，先掌握这些即可。

## 7. 把形状用到神经网络

一层网络写作 $\mathbf z=W\mathbf x+\mathbf b$。输入列向量d维，输出h维，则：

$$W\in\mathbb R^{h\times d},\quad\mathbf b\in\mathbb R^{h},\quad\text{参数量}=hd+h$$

为什么？W要把d维输入变成h维输出，所以有h行d列，共hd个权重；每个输出再加一个偏置，共h个。

**带算例**：输入3维、隐藏4维、输出2维的两层全连接网络，均含偏置。第一层参数 $4\times3+4=16$，第二层 $2\times4+2=10$，合计26。若代码把batch放在行，X为B×d，常写 $XW^{\mathsf T}$ 得到B×h；不能只背某一种写法。

## 8. 考前结论速查：把分散的规则放在一起

### ① 先区分：一般矩阵能用什么，方阵才能用什么

**做选择题先看前提，再认结论，最后用反例排除过强说法。** 这里把本单元需要用的规则集中列出；前面各节负责解释过程，这里可直接用于闭卷复述。

| 前提或对象 | 直接记住的结论 |
| --- | --- |
| A为m×n，B为n×p | AB合法，结果m×p；不能由此推出BA合法 |
| 普通矩阵加减 | 要求形状完全相同；NumPy广播要另按代码规则判断 |
| $A\in\mathbb R^{m\times n}$ | $0\le\operatorname{rank}(A)\le\min(m,n)$；秩不等于非零元素数 |
| 齐次方程 $A\mathbf x=\mathbf0$，x有n个分量 | 一定有零解；自由变量数为 $n-\operatorname{rank}(A)$ |
| $\operatorname{rank}(A)=n$，即满列秩 | 齐次方程只有零解；一般方程若有解则唯一 |
| $\operatorname{rank}(A)=m$，即满行秩 | 对任意m维b，$A\mathbf x=\mathbf b$都有解；不一定唯一 |
| **A为n×n方阵** | **可逆 ⇔ 秩为n ⇔ 行列式非零 ⇔ 齐次方程只有零解 ⇔ 没有0特征值** |

最后一行可直接用于第2-09题。它把第4节的秩与零空间、第5节的方程解、第6节的行列式与特征值连在一起。完整推导见第6节的第⑥部分。

### ② 非齐次方程：先判有解，再判唯一

记 $r=\operatorname{rank}(A)$，$r'=\operatorname{rank}([A\mid\mathbf b])$，n为未知数个数：

| 条件 | 在实数范围的解的情况 |
| --- | --- |
| $r<r'$ | 无解，消元会出现0=非零数 |
| $r=r'=n$ | 唯一解，没有自由变量 |
| $r=r'<n$ | 无穷多解，有n−r个自由变量 |

**别漏前半句“r=r'”。** 仅看到r小于n，不能直接说非齐次方程有无穷多解，它也可能无解。齐次方程则不会无解。

### ③ 运算规则：注意因子顺序

下表假设表达式维度合法；涉及逆矩阵时，还要求相关方阵可逆。

| 规则 | 易错点 |
| --- | --- |
| $(AB)C=A(BC)$ | 结合律只改括号，不换因子顺序 |
| $AB$通常不等于$BA$ | 矩阵乘法一般没有交换律 |
| $(A+B)^{\mathsf T}=A^{\mathsf T}+B^{\mathsf T}$ | 加法转置不反转相加顺序 |
| $(AB)^{\mathsf T}=B^{\mathsf T}A^{\mathsf T}$ | 乘积转置反转因子顺序 |
| $(AB)^{-1}=B^{-1}A^{-1}$ | 乘积求逆也反转因子顺序 |
| $(A^{\mathsf T})^{-1}=(A^{-1})^{\mathsf T}$ | 可逆时，求逆与转置可以交换操作顺序 |

### ④ 特征值与正定：哪些是等价，哪些只是必要条件

| 前提或说法 | 应记结论 |
| --- | --- |
| $A\mathbf v=\lambda\mathbf v$，$\mathbf v\ne\mathbf0$ | v是对应lambda的特征向量；lambda可以为0 |
| 方阵的迹、行列式 | 分别等于全部特征值的和、积，按代数重数计，必要时含复特征值 |
| 三角矩阵，包括对角矩阵 | 特征值就是主对角线元素；一般矩阵不能直接这样读 |
| **实对称矩阵** | 正定 ⇔ 全部特征值大于0；半正定 ⇔ 全部特征值大于等于0 |
| 正定实对称矩阵 | 一定可逆，且对角线都为正 |
| 方阵可逆 | 不保证正定，例如 $\operatorname{diag}(-2,3)$ |
| 实对称矩阵对角线全正 | 不保证正定，例如 $\begin{pmatrix}1&2\\2&1\end{pmatrix}$ |
| 至少一个非零特征值 | 不保证可逆，例如 $\operatorname{diag}(1,0)$ |
| 行列式大于0 | 不保证正定，例如 $\operatorname{diag}(-1,-1)$；但能保证方阵可逆 |

本表中“三角矩阵的特征值”可从特征方程看出：$A-\lambda I$仍为三角矩阵，它的行列式是各项 $(a_{ii}-\lambda)$ 的乘积，令其为0便得到对角线上的数。

### ⑤ 最后做三个口头判断

“齐次方程有零解”能否推出可逆？不能，所有齐次方程都有零解，必须是**只有零解**，且讨论通常的双侧逆时A要是方阵。

“至少一个非零特征值”能否推出可逆？不能，必须是**没有0特征值**。拿diag(1,0)反驳。

“3×5矩阵满行秩”能否推出唯一解？不能。任意三维b都有解，但有5−3=2个自由变量，所以每个b都有无穷多解。

给出A、B的形状，能否立即判断AB与BA？秩和非零元素数为什么不同？3×5满行秩为何有解但不唯一？2×2可逆怎么判断？网络参数量为什么需要加偏置？

梯度与反向传播在单元④展开。
