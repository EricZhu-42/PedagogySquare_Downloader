<p align="center">

  <img alt="GitHub" src="https://img.shields.io/github/license/EricZhu-42/PedagogySquare_Downloader">
  <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/EricZhu-42/PedagogySquare_Downloader">	
  <img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/EricZhu-42/PedagogySquare_Downloader">
  <img alt="GitHub code size in bytes" src="https://img.shields.io/github/languages/code-size/EricZhu-42/PedagogySquare_Downloader">
  <img alt="GitHub top language" src="https://img.shields.io/github/languages/top/EricZhu-42/PedagogySquare_Downloader">
  </br>
  <img alt="GitHub stars" src="https://img.shields.io/github/stars/EricZhu-42/PedagogySquare_Downloader">
  <img alt="GitHub All Releases" src="https://img.shields.io/github/downloads/EricZhu-42/PedagogySquare_Downloader/total">
  <img alt="GitHub issues" src="https://img.shields.io/github/issues-raw/EricZhu-42/PedagogySquare_Downloader">
  <img alt="GitHub closed issues" src="https://img.shields.io/github/issues-closed-raw/EricZhu-42/PedagogySquare_Downloader">
  <img alt="PRs welcome" src="https://img.shields.io/badge/PRs-welcome-brightgreen">

</p>

# 教学立方课件下载器

在线教学平台——[教学立方](https://teaching.applysquare.com)的课件批量下载脚本，基于**Python** + **Requests**

> 创建日期：2020-03-30  
> 更新日期：2021-02-28

## 版本更新信息（重要！）

1. 已于2020年9月14日晚发布最新版本的release包，请**于9月14日前获取代码**的同学重新[下载脚本](https://github.com/EricZhu-42/PedagogySquare_Downloader/releases/download/v1.4_stable/PedagogySquare_Downloader_20200914.zip)。

2. 已**修复教学立方版本更新导致无法正常下载课件的问题**，且进行了稳定性优化。

3. 当前版本的脚本**解除了先前版本对ChromeDriver与Selenium的依赖**，目前**仅需安装Requests即可正常使用**。

   > 如果更新后的脚本无法正常使用，请尝试回退至[旧版本](https://github.com/EricZhu-42/PedagogySquare_Downloader/releases/download/v1.3_stable/PedagogySquare_Downloader_20200702.zip)，观察问题是否解决，并联系开发者反馈问题，感谢！

## 程序特色

1. **一键下载**所有课程的全部课件，方便快捷
2. **可下载未直接开放下载的课件**，视频等内容
3. **可深度配置**的课程筛选/文件拓展名筛选功能

以下为运行过程中控制台截图示例：

![](./figure/1.png)

> 本程序旨在方便学生下载教学立方平台上的课件及相关教学资料，消除下载文件的重复劳动  
> 请尊重教师的知识产权与劳动成果。除非获得教师许可，请勿将下载得到的文件在互联网上进行传播  
> 如本程序损害了您的权益，请联系作者删除相关代码  

## 运行环境

开发过程中使用的环境与第三方模块版本如下：

- **Python** = 3.7.4

- **Requests** = 2.22.0

为了正常运行脚本，请安装**不低于**以上版本的Python与Requests

> 另：经测试，**该脚本可在移动端的终端模拟器中正常运行**；安卓平台执行Python脚本可以参考[@OrangeX4](https://github.com/OrangeX4)提供的[工具与教程]。(https://orangex.orangex4.cool/)

## 使用方法

### 1. 配置环境（请参考其他教程）

1. 安装对应版本的Python

2. 安装对应版本的Python模块：Requests（推荐使用[Anaconda](https://www.anaconda.com/)进行管理）


### 2. 修改配置文件

修改文件 `config.json` ，填入用户名、密码等信息

> 关于如何修改配置文件，请参考”最简配置方案“一章  
> 关于配置文件内各项参数的说明，请参考”配置文件说明“一章  

### 3. 运行脚本

运行 `download.py`  

> 注：若运行过程中出现下载速度过慢等现象，可能是由于与教学立方网站连接不稳定，请尝试重新运行脚本。

## 项目结构介绍

| 文件名              | 功能                     |
| ------------------- | ------------------------ |
| figure/             | 脚本说明中用到的图片文件 |
| download.py         | 脚本运行入口             |
| config.json         | 执行参数的配置文件       |
| config_example.json | 供参考的样例配置文件     |

## 最简配置方案

```json
{
	"username": "your_username",
	"password": "your_password",
	"download_all_ext": true,
	"download_all_courses": true,
	"ext_list": [],
	"ext_expel_list": [],
	"cid_list": []
}
```

将 `your_username` 与 `your_password` （**保留双引号**）替换成你的**手机号**和**教学立方登录密码**即可，其他参数无需修改。

> 请确保json文件格式正确，可参考提供的 `config_example.json` 进行配置。

## 配置文件说明

以下对 `config.json` 内各项参数进行简要说明：

| 参数名               | 类型 | 含义                                                |
| -------------------- | ---- | --------------------------------------------------- |
| username             | str  | 教学立方登录用户名（一般为手机号）                  |
| password             | str  | 教学立方登录密码                                    |
| download_all_ext     | bool | 是否下载所有类型的文件                              |
| download_all_courses | bool | 是否下载所有课程的课件                              |
| ext_list             | list | 下载文件的类型（如：pdf，docx，zip）                |
| ext_expel_list       | list | 排除文件的类型                                      |
| cid_list             | list | 需要下载的课程ID                                    |

#### 注意：

1. 文件类型参数优先级为：`ext_expel_list` > `download_all_ext` > `ext_list`  
   如：若希望下载“除了zip格式文件外的所有类型文件“，应设置参数为

   - `download_all_ext` = `true`
   - `ext_expel_list` = `["zip"]`

2. 课程ID在课程主页地址中查看，例如：  
   ![](./figure/0.png)  
   图中对应课程的ID为**8261**  


## 版权信息

联系邮箱：zhuxinhao00@gmail.com

本项目基于MIT协议开源
