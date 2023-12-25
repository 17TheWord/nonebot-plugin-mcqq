import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="nonebot-plugin-mcqq",
    version="2.5.2",
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
        'mcqq-tool>=1.0.1',
        'nonebot2>=2.0.0',
        'nonebot2[websockets]',
        'nonebot2[fastapi]',
        'nonebot-adapter-onebot>=2.1.1',
        'nonebot-adapter-qq>=1.1.2',
        'nonebot-plugin-guild-patch>=0.2.0',
        'aio-mc-rcon>=3.2.0'
    ]
)
