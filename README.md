# 项目介绍 #

该项目实现了python自动抢注甲骨文（ORACLE CLOUD）云免费服务器，可通过telegram实时发送信息查看抢注结果

该项目适合成功注册了甲骨文云账号但是在申请免费云服务器遇到了以下问题

```text
API 错误
可用性域 VM.Standard.A1.Flex 中配置 AD-1 的容量不足。请在其他可用性域中创建实例，或稍后重试。如果指定了容错域，请尝试在不指定容错域的情况下创建实例。如果这样不起作用，请稍后重试
```

最新发布2026年4月28日，亲测可用！！！

# ORACLE CLOUD 准备工作 #

## 一、获取自己账号的相关信息 ##

1. 登录到甲骨文云主页

```txt
左上角三条杠 -> 实例 -> 创建实例
```

2. 根据自己的需要选择映像和配置，CPU最高可以选择Ampere的4核24G

```txt
另存为堆栈 -> 配置默认就行 -> 下载Terraform
```

3. 得到一个压缩包,解压之后会得到`main.tf`文件

## 二、获取子网OCID信息 ##

1. 登录到甲骨文云主页

```text
左上角三条杠 -> 网络 (Networking) -> 虚拟云网络 (Virtual Cloud Networks) -> 操作 ->启动VCN向导 -> 
选择第一个(创建具有 Internet 连接的 VCN) -> 启动 VCN 向导
```

2. 配置VCN基本信息

- VCN名称（VCN Name）：随便填，比如填 vcn-20260428
- 区间（Compartment）：这个非常重要！必须选择你抢机器脚本里配置的那个 Compartment。也就是确保它和你脚本里配置的一致。
- 其他默认即可

3. 点击创建

4. 获取真实的`子网OCID`

```text
找到创建的VCN(vcn-20260428) -> (顶部)子网 -> 公共子网 -> 子网信息处获取子网的OCID
```

## 三、获取甲骨文API秘钥 ##

1. 登录到甲骨文云主页

```text
右上角头像 -> 点击自己的邮箱 -> 顶上令牌和密钥 -> 添加API秘钥
```

2. 下载并保存密钥和配置文件

- 选择生成API秘钥对
- 下载私有秘钥，会得到`***.pem`文件
- 点击添加会弹出"配置文件预览"，复制`配置文件预览内容`并保存



# 填入参数到python项目中 #

## 一、填入文件信息 ##

- 将`配置文件预览内容`填入到项目的`config`文件中
  - 注意：最后一行保留为`key_file=oci_private_key.pem`,即`删除配置文件预览内容`的最后一行改为`key_file=oci_private_key.pem`
- 将秘钥文件`***.pem`粘贴到项目的`oci_private_key.pem`中

##  二、根据`main.tf`填入参数 ##

```python
#22行~27行
instance_display_name = 'ins****'	#对应main.tf第63行display_name
compartment_id = 'oci*******'		#对应main.tf第56行compartment_id 
domain = "***********"			    #对应main.tf第55行availability_domain
image_id = "oci********"			#对应main.tf第79行source_id
ssh_key = "ssh**********"			#对应main.tf第69行ssh_authorized_keys
```

## 三、根据`子网OCID`填入subnet_id ##

```python
#30行
subnet_id = 'ocid****************'
```

# （进阶可选）通过telegram（后面简称tg）实时发送消息 #

## 一、创建机器人

1. 在tg搜索`@BotFather`，认准蓝V标识

2. 输入`/newbot`

3. 此时需要输入机器人name，类似于用户名

4. 然后输入机器人的username，必须以`_bot`结尾，类似于id（后续通过id添加机器人）

5. 此时会得到一串`HTTP API`将其填入

   ```python
   #38行
   bot_api = '*********'
   ```

## 二、获取id

1. 在tg搜索`@get_id_bot`并添加

2. 若提示Please join first:需点击链接加入频道

3. 再次回到`@get_id_bot`机器人发送`/start`,选择`My Id`即可获取id

4. 填入项目之中

   ```python
   #39行
   chat_id = '*********'
   ```

   
