# AI漫文老司机
基于Stable Diffusion WebUI 的网文生成动漫短视频使用的插件

还在持续更新中

## 安装方法

### 方法1: WebUi 中 Extensions(插件)/Install From Url(通过Url安装) 安装

URL for extension's git repository(通过资源安装)中输入 git url

```
https://github.com/codewithevan/mecreater.git
```
点击[Install]即可安装

### 方法2: 使用 git clone(git 克隆)

进入 WebUi 目录 下，cmd 界面中，运行

```
git clone https://github.com/codewithevan/mecreater.git
```
即可安装


### 方法3: 插件包下载安装

点击右上角 

<img width="176" alt="image" src="https://github.com/codewithevan/mecreater/assets/4951627/a92e42f0-b515-462c-a721-eb917ff14a69">

<img width="505" alt="image" src="https://github.com/codewithevan/mecreater/assets/4951627/2fea8550-d9ba-4db0-8fd6-5bd1071de843">

下载插件包到WebUi 目录  /extensions 下即可

## 因为插件不断在迭代，请尽量保持最新版本，可以使用以下方法更新插件

### 方法1: WebUi 插件更新

在WebUi界面中中 Extensions(插件)/Check for updates(检查更新)

会自动检查最新的代码并下载更新

### 方法2: git pull 更新

进入WebUi 目录  /extensions/mecreater 运行命令

```
git pull
```

即可完成更新


### 使用方法
## 分镜控制
1.直接在正向提示词中输入分镜脚本（需要时英文）

2.每个分镜一行

3.分镜数量必须与批次数量匹配，

如:16个分镜，就设置 批次(Batch count) 2，单批数量(Batch size) 8

