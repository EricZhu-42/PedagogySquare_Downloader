# 教学立方课件下载器

在线教学平台——[教学立方](teaching.applysquare.com)的课件批量下载脚本

> 更新日期：2020-03-31

## 软件特色



## 使用说明

1. 配置Python环境

- Python 3.7.4
- Requests 2.22.0
- Selenium 3.141.0
  - 基于Chrome + ChromeDriver，其中Chrome版本75.0.3770.142，ChromeDriver版本与Chrome一致

	2. 修改配置文件 `config.json` ，填入用户名、密码等信息
 	3. 运行 `download.py` 

## 项目结构介绍

| 文件名              | 功能               |
| ------------------- | ------------------ |
| download.py         | 脚本执行入口       |
| config.json         | 执行参数的配置文件 |
| config_example.json | 样例配置文件       |

## 配置文件说明

以下对 `config_example.json` 内各项参数进行简要说明：

| 参数名               | 类型 | 含义                                                |
| -------------------- | ---- | --------------------------------------------------- |
| username             | str  | 教学立方登录用户名（一般为手机号）                  |
| password             | str  | 教学立方登录密码                                    |
| headless_mode        | bool | 是否启用WebDriver的headless模式（运行时不显示界面） |
| download_all_ext     | bool | 是否下载所有类型的文件                              |
| download_all_courses | bool | 是否下载所有课程的课件                              |
| ext_list             | list | 下载文件的类型（如：pdf，docx，zip）                |
| ext_expel_list       | list | 排除文件的类型                                      |
| cid_list             | list | 需要下载的课程ID                                    |

#### 注意：

1. 文件类型参数优先级为：`ext_expel_list` > `download_all_ext` > `ext_list`
   即：若希望下载“除了zip格式文件外的所有类型文件“，应设置参数为

   1. `download_all_ext` = `true`
   2. `ext_list` = `[zip]`

2. 课程ID在课程主页地址中查看
   ![image-20200331150145159](C:\Users\Null_42\AppData\Roaming\Typora\typora-user-images\image-20200331150145159.png)
   如图，对应的课程id为**8261**

   

## 版权信息

#### 作者：
