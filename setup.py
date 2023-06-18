import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="nonebot-plugin-mcqq",
    version="1.2.2",
    author="17TheWord",
    author_email="17theword@gmail.com",
    description="基于NoneBot的QQ群聊与Minecraft Server消息互通插件",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/17TheWord/nonebot-plugin-mcqq",
    packages=["nonebot_plugin_mcqq"],
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent"
    ],
    install_requires=[
        'mcqq-tool>=0.0.5',
        'nonebot2>=2.0.0',
        'nonebot-adapter-onebot>=2.1.1',
        'nonebot-plugin-guild-patch>=0.2.0',
        'websockets>=10.3',
        'aio-mc-rcon>=3.2.0'
    ]
)
