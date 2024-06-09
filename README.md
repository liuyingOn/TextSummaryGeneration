本系统使用PyInstaller来进行打包，使用指令为
pyinstaller -F --add-data "textrank4zh:textrank4zh" --collect-all snownlp --collect-all jieba .\project_main.py
意味生成可执行文件，打包textrank4zh模块，snownlp 和jieba的全部模块 ，以及其他部分依赖模块。
需要默认文件pdf放在可执行文件同目录下运行默认命令
