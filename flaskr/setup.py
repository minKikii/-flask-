#这个模块用于发布包
from setuptools import find_packages,setup
#setuptools跟pip一样都是包管理工具，可以将包注册到安装的Python环境中
#https://blog.csdn.net/pfm685757/article/details/48651389
setup(
    name='flaskr', #应用名称
    version='1.0.2',#版本号
    #这两个会在打包时自动生成为你的项目名(flaskr-0.52)
    packages=find_packages(),

    #当你的每个package下的__init__.py里都import了当前package下的module时，find_packages()会自动帮你找到所有的包。
    include_package_data=True,
    #告诉 distribute 自动查找一个 MANIFEST.in 文件。 解析此文件获得有效的包类型的数据，并安装所有这些包。
    #据说这个参数的默认值就是True
    #这个必须设置为True否则MANIFEST.in会失去效果
    zip_safe=False,
    #默认值为False，在每次生成egg包的时候检查项目文件的内容
    install_requires=['flask',],
    #离线安装
)